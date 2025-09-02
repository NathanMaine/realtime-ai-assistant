# API Documentation for Real-Time AI Meeting Assistant

## Overview
The Real-Time AI Meeting Assistant provides both HTTP and WebSocket APIs for audio processing, transcription, and AI-powered analysis.

## HTTP Endpoints

### GET /
**Description**: Serves the main web interface
**Response**: HTML page with the meeting assistant interface
**Content-Type**: text/html

## WebSocket Endpoint

### WebSocket /ws
**Description**: Real-time audio processing and communication
**Protocol**: WebSocket
**URL**: `ws://localhost:8000/ws`

## WebSocket Message Protocol

### Client to Server Messages

#### Start Recording
```json
"start_recording"
```
**Description**: Initiates continuous audio recording with VAD
**Response**: Server acknowledges with status update

#### Stop Recording
```json
"stop_recording"
```
**Description**: Stops audio recording and processes remaining audio
**Response**: Server acknowledges with status update

#### Audio Data
```json
"audio:[base64-encoded-audio-data]"
```
**Description**: Sends audio data for processing
**Format**: Base64 encoded audio (WebM, WAV, or PCM)
**Processing**: Automatic VAD analysis and transcription

### Server to Client Messages

#### Status Updates
```json
{
  "status": "recording_started" | "recording_stopped" | "processing"
}
```
**Description**: Current recording/processing status

#### Processing Results
```json
{
  "transcription": "Transcribed text from audio",
  "summary": "AI-generated meeting summary",
  "actions": [
    {
      "task": "Task description",
      "assignee": "Person responsible",
      "due": "Due date or timeframe"
    }
  ]
}
```
**Description**: Complete processing results
**Fields**:
- `transcription`: Raw speech-to-text output
- `summary`: AI-generated meeting summary
- `actions`: Array of extracted action items

#### Error Messages
```json
{
  "error": "Error description message"
}
```
**Description**: Error notifications and troubleshooting information

## Audio Format Specifications

### Supported Input Formats
- **WebM**: From browser MediaRecorder API
- **WAV**: Standard audio format
- **Raw PCM**: 16-bit, 16kHz, mono from Web Audio API

### Processing Requirements
- **Sample Rate**: 16kHz (automatically resampled if needed)
- **Channels**: Mono (single channel)
- **Bit Depth**: 16-bit PCM
- **Encoding**: Base64 for WebSocket transmission

## VAD (Voice Activity Detection) Parameters

### Configuration
- **VAD_AGGRESSIVENESS**: 0-3 (sensitivity level)
- **SILENCE_THRESHOLD**: Frames of silence (default: 50 = 1.5s)
- **FRAME_DURATION**: Analysis window (30ms)

### Behavior
- Speech detection triggers audio accumulation
- Silence threshold determines segment boundaries
- Automatic segmentation for optimal transcription

## Error Handling

### Common Error Codes
- **Microphone Access Denied**: Check browser permissions
- **WebSocket Connection Failed**: Verify server status
- **Audio Format Error**: Ensure 16kHz, 16-bit PCM
- **API Key Invalid**: Verify xAI API key
- **Model Load Failed**: Check GPU memory and model files

### Recovery Mechanisms
- Automatic fallback to CPU processing
- Graceful degradation for optional features
- Connection retry with exponential backoff
- Debug file generation for troubleshooting

## Rate Limiting

### API Limits
- xAI API: Follow rate limits specified by xAI
- WebSocket: No explicit rate limiting (real-time processing)
- File Processing: Sequential processing of audio segments

### Performance Considerations
- Audio segments processed sequentially
- GPU acceleration for AI models when available
- Memory usage scales with audio segment length

## Security

### Authentication
- API keys stored in environment variables
- No user authentication (localhost development)
- WebSocket origin validation

### Data Privacy
- Audio processed locally when possible
- API communications use HTTPS
- Debug files contain audio data (use caution)

## Monitoring

### Debug Features
- Audio file generation: `debug_audio_[timestamp].wav`
- VAD logging: Speech detection status
- Performance metrics: Processing times
- Error logging: Comprehensive error tracking

### Health Checks
- WebSocket connection status
- API key validation
- Model loading status
- Audio device availability

## Examples

### Basic Usage Flow
1. Connect to WebSocket: `ws://localhost:8000/ws`
2. Send: `"start_recording"`
3. Receive: `{"status": "recording_started"}`
4. Send audio data: `"audio:[base64-data]"`
5. Receive results: `{"transcription": "...", "summary": "...", "actions": [...]}`

### JavaScript Client Example
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

// Handle connection
ws.onopen = () => {
    console.log('Connected to server');
};

// Handle messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.status) {
        console.log('Status:', data.status);
    } else if (data.transcription) {
        console.log('Transcription:', data.transcription);
    }
};

// Start recording
ws.send('start_recording');

// Send audio data
const audioData = getAudioData(); // Your audio capture logic
ws.send('audio:' + btoa(audioData));
```

## Version History

### v4.0 (Current)
- Added VAD with configurable parameters
- Real-time WebSocket processing
- Enhanced audio format support
- Improved error handling

### v3.0
- Converted to FastAPI with WebSocket support
- Added web-based UI
- Enhanced real-time communication

### v2.0
- Added speaker diarization
- Improved AI summarization
- Enhanced user interface

### v1.0
- Basic transcription and summarization
- Streamlit-based interface
- Core functionality implementation
