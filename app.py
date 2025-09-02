from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pyaudio
import wave
import whisper
import requests
import pyttsx3
import pandas as pd
import numpy as np
import os
import torch
import json
from dotenv import load_dotenv
import asyncio
import base64
import io
from pyannote.audio import Pipeline
import torchaudio
import webrtcvad
import struct
import time

# Load environment variables
load_dotenv()

# --- Global Constants & Initialization ---
API_KEY = os.getenv("XAI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")  # For pyannote.audio
if not API_KEY:
    print("Warning: XAI_API_KEY not found in .env file. LLM features will be disabled.")
if not HF_TOKEN:
    print("Warning: HF_TOKEN not found. Speaker diarization will be disabled.")
API_URL = "https://api.x.ai/v1/chat/completions"
MODEL_RATE = 16000
FILENAME_WAV = "temp_audio.wav"
FILENAME_WEBM = "temp_audio.webm"

# VAD settings
VAD_AGGRESSIVENESS = 1  # Reduced from 3 to 1 (less aggressive, more sensitive to speech)
SILENCE_THRESHOLD = 50  # Increased from 30 to 50 frames (1.5 seconds of silence)
FRAME_DURATION = 30  # ms, must be 10, 20, or 30
FRAME_SIZE = int(MODEL_RATE * FRAME_DURATION / 1000) * 2  # 16-bit samples, so *2 for bytes

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Cache expensive resources ---
whisper_model = None
tts_engine = None
diarization_pipeline = None
vad = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        whisper_model = whisper.load_model("base", device="cuda" if torch.cuda.is_available() else "cpu")
    return whisper_model

def get_tts_engine():
    global tts_engine
    if tts_engine is None:
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', 180)
    return tts_engine

def get_diarization_pipeline():
    global diarization_pipeline
    if diarization_pipeline is None and HF_TOKEN:
        try:
            print("Loading speaker diarization pipeline...")
            diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HF_TOKEN)
            if torch.cuda.is_available():
                diarization_pipeline.to(torch.device("cuda"))
            print("Speaker diarization pipeline loaded successfully.")
        except Exception as e:
            print(f"Failed to load diarization pipeline: {e}")
            print("Speaker diarization will be disabled.")
            diarization_pipeline = None
    return diarization_pipeline

def get_vad():
    global vad
    if vad is None:
        vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
    return vad

class AudioSession:
    def __init__(self):
        self.audio_buffer = bytearray()  # For incoming audio frames
        self.speech_buffer = bytearray()  # For accumulating speech audio
        self.silence_frames = 0
        self.is_speaking = False
        self.last_processed_time = 0

# Global session storage (in production, use a proper session manager)
sessions = {}

# --- Core Functions ---
def process_vad_frame(frame_data):
    """Process a 10/20/30ms frame with VAD. Returns True if speech detected."""
    vad_instance = get_vad()
    try:
        return vad_instance.is_speech(frame_data, MODEL_RATE)
    except Exception as e:
        print(f"VAD error: {e}")
        return False

async def process_audio_segment(audio_data: bytes, websocket: WebSocket):
    """Processes accumulated audio segment and sends result via WebSocket."""
    try:
        print(f"Processing audio segment of length: {len(audio_data)} bytes")
        
        # Debug: Check first few bytes of audio data
        if len(audio_data) > 0:
            print(f"First 20 bytes of audio data: {audio_data[:20].hex()}")
        if len(audio_data) >= 44:
            print(f"Possible WAV header: {audio_data[:44].hex()}")
        
        # Check format
        if audio_data[:4] == b'RIFF':
            # WAV format
            filename = FILENAME_WAV
            with open(filename, 'wb') as f:
                f.write(audio_data)
        elif audio_data[:4] == b'\x1a\x45\xdf\xa3':
            # WebM format
            filename = FILENAME_WEBM
            with open(filename, 'wb') as f:
                f.write(audio_data)
        else:
            # Assume raw PCM, create WAV
            filename = FILENAME_WAV
            wav_data = create_wav_from_pcm(audio_data)
            with open(filename, 'wb') as f:
                f.write(wav_data)
        
        print("Audio file saved, loading Whisper model...")
        
        # Check if file exists and has content
        if not os.path.exists(filename):
            print(f"Error: Audio file {filename} was not created")
            return
            
        file_size = os.path.getsize(filename)
        print(f"Audio file size: {file_size} bytes")
        
        # Check minimum audio length (roughly 0.5 seconds of audio data)
        min_audio_size = 44 + (16000 * 0.5 * 2)  # WAV header + 0.5s of 16-bit audio
        if file_size < min_audio_size:
            print(f"Audio file too small ({file_size} bytes, need at least {min_audio_size} bytes for 0.5s), skipping transcription")
            return
        
        # Debug: Save a copy of the audio file for inspection
        debug_filename = f"debug_audio_{int(time.time())}.wav"
        import shutil
        shutil.copy(filename, debug_filename)
        print(f"Debug audio file saved as: {debug_filename}")
        
        # Transcribe with segments
        model = get_whisper_model()
        result = model.transcribe(filename, fp16=False)
        transcribed_text = result.get("text", "").strip()
        segments = result.get("segments", [])
        
        print(f"Transcription result: '{transcribed_text}'")
        print(f"Number of segments: {len(segments)}")
        if segments:
            print(f"First segment: {segments[0]}")
        
        # Perform speaker diarization if available
        diarized_text = transcribed_text
        if HF_TOKEN and segments:
            pipeline = get_diarization_pipeline()
            if pipeline is not None:
                try:
                    # Load audio for diarization
                    waveform, sample_rate = torchaudio.load(filename)
                    if sample_rate != 16000:
                        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                        waveform = resampler(waveform)
                    
                    # Perform diarization
                    diarization = pipeline({"waveform": waveform, "sample_rate": 16000})
                    
                    # Assign speakers to segments
                    diarized_segments = []
                    for segment in segments:
                        start = segment['start']
                        end = segment['end']
                        text = segment['text'].strip()
                        if text:
                            # Find the speaker for this segment
                            speakers = []
                            for turn, _, speaker in diarization.itertracks(yield_label=True):
                                if turn.start <= start < turn.end or turn.start < end <= turn.end or (start <= turn.start and end >= turn.end):
                                    speakers.append(speaker)
                            speaker = speakers[0] if speakers else "Unknown"
                            diarized_segments.append(f"{speaker}: {text}")
                    
                    diarized_text = " ".join(diarized_segments)
                    print(f"Diarized text: '{diarized_text}'")
                except Exception as e:
                    print(f"Diarization error: {e}")
                    print("Falling back to regular transcription without speaker labels.")
            else:
                print("Diarization pipeline not available, using regular transcription.")
        
        if not diarized_text:
            print("No transcribed text found, sending empty result")
            await websocket.send_json({
                "transcription": "",
                "summary": "No speech detected in the audio segment.",
                "actions": []
            })
            return
        
        # Query LLM
        llm_response = await query_llm(diarized_text)
        if llm_response:
            result = {
                "transcription": diarized_text,
                "summary": llm_response.get("summary", ""),
                "actions": llm_response.get("actions", [])
            }
            await websocket.send_json(result)
            # Optionally, speak the summary
            if "summary" in result:
                engine = get_tts_engine()
                engine.say(result["summary"])
                engine.runAndWait()
        else:
            await websocket.send_json({"error": "Failed to get LLM response."})

    except Exception as e:
        print(f"Error in process_audio_segment: {e}")
        import traceback
        traceback.print_exc()
        await websocket.send_json({"error": f"Processing error: {str(e)}"})
    finally:
        # Clean up both possible files
        for f in [FILENAME_WAV, FILENAME_WEBM]:
            if os.path.exists(f):
                os.remove(f)

def create_wav_from_pcm(pcm_data: bytes, sample_rate: int = MODEL_RATE, channels: int = 1, bits_per_sample: int = 16):
    """Create WAV data from raw PCM bytes."""
    data_size = len(pcm_data)
    file_size = 36 + data_size
    
    # WAV header
    header = struct.pack('<4sL4s4sLHHLLHH4sL',
                         b'RIFF', file_size, b'WAVE', b'fmt ', 16,
                         1, channels, sample_rate, sample_rate * channels * bits_per_sample // 8,
                         channels * bits_per_sample // 8, bits_per_sample, b'data', data_size)
    
    return header + pcm_data

async def process_audio(audio_data: bytes):
    """Processes audio data and returns transcription and LLM response."""
    try:
        print(f"Received audio data of length: {len(audio_data)} bytes")
        
        # Check if it's a WAV file (starts with RIFF)
        if len(audio_data) > 12 and audio_data[:4] == b'RIFF':
            print("Detected WAV format")
            filename = FILENAME_WAV
            # Save as WAV
            with open(filename, 'wb') as f:
                f.write(audio_data)
        else:
            print("Detected non-WAV format, saving as WebM")
            filename = FILENAME_WEBM
            # Save as WebM
            with open(filename, 'wb') as f:
                f.write(audio_data)
        
        print("Audio file saved, loading Whisper model...")
        
        # Transcribe with segments
        model = get_whisper_model()
        result = model.transcribe(filename, fp16=False)
        transcribed_text = result.get("text", "").strip()
        segments = result.get("segments", [])
        
        print(f"Transcription result: '{transcribed_text}'")
        
        # Perform speaker diarization if available
        diarized_text = transcribed_text
        if HF_TOKEN and segments:
            pipeline = get_diarization_pipeline()
            if pipeline is not None:
                try:
                    # Load audio for diarization
                    waveform, sample_rate = torchaudio.load(filename)
                    if sample_rate != 16000:
                        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                        waveform = resampler(waveform)
                    
                    # Perform diarization
                    diarization = pipeline({"waveform": waveform, "sample_rate": 16000})
                    
                    # Assign speakers to segments
                    diarized_segments = []
                    for segment in segments:
                        start = segment['start']
                        end = segment['end']
                        text = segment['text'].strip()
                        if text:
                            # Find the speaker for this segment
                            speakers = []
                            for turn, _, speaker in diarization.itertracks(yield_label=True):
                                if turn.start <= start < turn.end or turn.start < end <= turn.end or (start <= turn.start and end >= turn.end):
                                    speakers.append(speaker)
                            speaker = speakers[0] if speakers else "Unknown"
                            diarized_segments.append(f"{speaker}: {text}")
                    
                    diarized_text = " ".join(diarized_segments)
                    print(f"Diarized text: '{diarized_text}'")
                except Exception as e:
                    print(f"Diarization error: {e}")
                    print("Falling back to regular transcription without speaker labels.")
                    # Fall back to original text
            else:
                print("Diarization pipeline not available, using regular transcription.")
        
        if not diarized_text:
            return {"error": "No speech detected. Please speak clearly and ensure your microphone is working."}

        # Query LLM
        llm_response = await query_llm(diarized_text)
        if llm_response:
            return {
                "transcription": diarized_text,
                "summary": llm_response.get("summary", ""),
                "actions": llm_response.get("actions", [])
            }
        else:
            return {"error": "Failed to get LLM response."}

    except Exception as e:
        print(f"Error in process_audio: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Processing error: {str(e)}"}
    finally:
        for f in [FILENAME_WAV, FILENAME_WEBM]:
            if os.path.exists(f):
                os.remove(f)

async def query_llm(text):
    """Sends transcription to the LLM and returns the parsed response."""
    if not API_KEY:
        # Return dummy response for testing
        return {
            "summary": f"Summary: {text[:100]}...",
            "actions": [{"task": "Test action", "assignee": "User", "due": "Today"}]
        }
    
    prompt = f'You are a meeting assistant. The following text includes speaker labels (e.g., SPEAKER_00, SPEAKER_01). Summarize the meeting content, considering different speakers for richer context, and extract action items. Format your response as a JSON object with two keys: "summary" and "actions". The "actions" array should contain objects with "task", "assignee", and "due" keys.\n\nText: {text}'
    payload = {"model": "grok-3", "messages": [{"role": "user", "content": prompt}]}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        llm_output_str = data['choices'][0]['message']['content']
        return json.loads(llm_output_str)
    except Exception as e:
        print(f"API Error: {e}")
        return None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = id(websocket)  # Simple session ID
    sessions[session_id] = AudioSession()
    session = sessions[session_id]
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received WebSocket data: {data[:100]}...")  # Log first 100 chars
            
            if data == "start_recording":
                # Reset session for new recording
                session.audio_buffer.clear()
                session.speech_buffer.clear()
                session.silence_frames = 0
                session.is_speaking = False
                await websocket.send_json({"status": "recording_started"})
            
            elif data == "stop_recording":
                # Process any remaining audio
                if session.speech_buffer:
                    wav_data = create_wav_from_pcm(bytes(session.speech_buffer))
                    await process_audio_segment(wav_data, websocket)
                session.audio_buffer.clear()
                session.speech_buffer.clear()
                await websocket.send_json({"status": "recording_stopped"})
            
            elif data.startswith("audio:"):
                # Decode base64 audio data
                audio_b64 = data[6:]
                audio_data = base64.b64decode(audio_b64)
                
                # Check format and handle accordingly
                if audio_data[:4] == b'RIFF':
                    # This is WAV data from Web Audio API
                    pcm_data = audio_data[44:]  # Skip WAV header
                elif audio_data[:4] == b'\x1a\x45\xdf\xa3':
                    # This is WebM data from MediaRecorder fallback
                    print("Received WebM data, processing directly")
                    # Process WebM data directly (without VAD for simplicity)
                    await process_audio_segment(audio_data, websocket)
                    continue
                else:
                    # Assume it's raw PCM data from Web Audio API
                    pcm_data = audio_data
                
                # Accumulate PCM data
                session.audio_buffer.extend(pcm_data)
                
                # Process in frames for VAD (30ms frames at 16000Hz = 480 samples = 960 bytes for 16-bit)
                frame_size_bytes = FRAME_SIZE
                while len(session.audio_buffer) >= frame_size_bytes:
                    frame = session.audio_buffer[:frame_size_bytes]
                    session.audio_buffer = session.audio_buffer[frame_size_bytes:]
                    
                    is_speech = process_vad_frame(frame)
                    
                    if is_speech:
                        session.is_speaking = True
                        session.silence_frames = 0
                        # Accumulate speech frames
                        session.speech_buffer.extend(frame)
                        print(f"VAD: Speech detected, buffer size: {len(session.speech_buffer)} bytes")
                    else:
                        if session.is_speaking:
                            session.silence_frames += 1
                            # Still accumulate silence frames to maintain continuity
                            session.speech_buffer.extend(frame)
                            print(f"VAD: Silence frame {session.silence_frames}/{SILENCE_THRESHOLD}, buffer size: {len(session.speech_buffer)} bytes")
                            
                            # If enough silence frames, process the accumulated speech segment
                            if session.silence_frames >= SILENCE_THRESHOLD:
                                # Process accumulated speech audio
                                if len(session.speech_buffer) > 0:
                                    # Create WAV from accumulated speech PCM
                                    wav_data = create_wav_from_pcm(bytes(session.speech_buffer))
                                    await process_audio_segment(wav_data, websocket)
                                
                                # Reset for next segment
                                session.speech_buffer.clear()
                                session.is_speaking = False
                                session.silence_frames = 0
                                print("VAD: Speech segment completed, resetting for next segment")
            
            elif data.startswith("chunk:"):
                # For compatibility, handle old format
                audio_b64 = data[6:]
                audio_data = base64.b64decode(audio_b64)
                result = await process_audio(audio_data)
                await websocket.send_json(result)
                # Speak summary
                if "summary" in result:
                    engine = get_tts_engine()
                    engine.say(result["summary"])
                    engine.runAndWait()
                    
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        # Clean up session
        if session_id in sessions:
            del sessions[session_id]

@app.get("/", response_class=HTMLResponse)
async def get():
    with open("static/index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000
        # Temporarily disabled SSL for testing
        # ssl_keyfile="key.pem",
        # ssl_certfile="cert.pem"
    )
