from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
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

# Load environment variables
load_dotenv()

# --- Global Constants & Initialization ---
API_KEY = os.getenv("XAI_API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file. Please set XAI_API_KEY.")
API_URL = "https://api.x.ai/v1/chat/completions"
MODEL_RATE = 16000
FILENAME = "temp_audio.wav"

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Cache expensive resources ---
whisper_model = None
tts_engine = None

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

# --- Core Functions ---
async def process_audio(audio_data: bytes):
    """Processes audio data and returns transcription and LLM response."""
    try:
        print(f"Received audio data of length: {len(audio_data)} bytes")
        
        # Check if it's a WAV file (starts with RIFF)
        if len(audio_data) > 12 and audio_data[:4] == b'RIFF':
            print("Detected WAV format")
            # Save as WAV
            with open(FILENAME, 'wb') as f:
                f.write(audio_data)
        else:
            print("Detected non-WAV format, attempting to convert")
            # Try to handle other formats (like WebM from MediaRecorder)
            # For now, just save as is and hope Whisper can handle it
            with open(FILENAME, 'wb') as f:
                f.write(audio_data)
        
        print("Audio file saved, loading Whisper model...")
        
        # Transcribe
        model = get_whisper_model()
        result = model.transcribe(FILENAME, fp16=False)
        transcribed_text = result.get("text", "").strip()
        
        print(f"Transcription result: '{transcribed_text}'")

        if not transcribed_text:
            return {"error": "No speech detected. Please speak clearly and ensure your microphone is working."}

        # Query LLM
        llm_response = await query_llm(transcribed_text)
        if llm_response:
            return {
                "transcription": transcribed_text,
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
        if os.path.exists(FILENAME):
            os.remove(FILENAME)

async def query_llm(text):
    """Sends transcription to the LLM and returns the parsed response."""
    prompt = f'You are a meeting assistant. Summarize the following text and extract action items. Format your response as a JSON object with two keys: "summary" and "actions". The "actions" array should contain objects with "task", "assignee", and "due" keys.\n\nText: {text}'
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
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received WebSocket data: {data[:100]}...")  # Log first 100 chars
            if data.startswith("audio:"):
                # Decode base64 audio data
                audio_b64 = data[6:]
                print(f"Audio base64 length: {len(audio_b64)}")
                audio_data = base64.b64decode(audio_b64)
                print(f"Decoded audio length: {len(audio_data)} bytes")
                result = await process_audio(audio_data)
                print(f"Processing result: {result}")
                await websocket.send_json(result)
                # Optionally, speak the summary
                if "summary" in result:
                    engine = get_tts_engine()
                    engine.say(result["summary"])
                    engine.runAndWait()
    except WebSocketDisconnect:
        print("WebSocket disconnected")

@app.get("/", response_class=HTMLResponse)
async def get():
    with open("static/index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
