# Architecture of Real-Time AI Meeting Assistant

## System Overview
The Real-Time AI Meeting Assistant is a sophisticated FastAPI-based application with WebSocket support that provides continuous voice activity detection, real-time audio transcription, intelligent summarization, and action item extraction. The system processes live audio streams using advanced AI models and provides immediate feedback through a modern web interface.

## Core Components

### 1. **Web Interface (Frontend)**
- **Technology**: HTML5, CSS3, Vanilla JavaScript with Web Audio API
- **Features**:
  - Real-time audio capture using `getUserMedia()` and `MediaRecorder`
  - Web Audio API for audio processing and resampling
  - WebSocket client for bidirectional communication
  - Responsive UI with status indicators and result display
  - Microphone testing and permission handling
  - Cross-browser compatibility (Chrome, Firefox, Edge, Safari)

### 2. **FastAPI Backend Server**
- **Technology**: FastAPI with WebSocket support, Uvicorn ASGI server
- **Endpoints**:
  - `GET /`: Serves the main web interface
  - `WebSocket /ws`: Handles real-time audio processing
  - Static file serving for CSS/JS assets
- **Features**:
  - Asynchronous request handling
  - CORS middleware for cross-origin requests
  - Session management for per-connection state
  - Error handling and logging

### 3. **Voice Activity Detection (VAD) Engine**
- **Technology**: WebRTC VAD with custom frame processing
- **Configuration**:
  - `VAD_AGGRESSIVENESS`: Sensitivity level (0-3, current: 1)
  - `SILENCE_THRESHOLD`: Frames before processing (current: 50 = 1.5s)
  - `FRAME_DURATION`: Analysis window (30ms)
- **Features**:
  - Real-time speech/silence detection
  - Automatic audio segmentation
  - Configurable sensitivity and timing
  - Debug logging for troubleshooting

### 4. **Audio Processing Pipeline**
- **Input Formats**: WebM (MediaRecorder), WAV, Raw PCM (Web Audio API)
- **Processing Steps**:
  1. Base64 decoding of WebSocket audio data
  2. Format detection and conversion to WAV
  3. Audio validation (minimum length checks)
  4. Sample rate verification (16kHz required)
- **Features**:
  - Multi-format audio support
  - Automatic format conversion
  - Audio quality validation
  - Debug file generation

### 5. **Speech Recognition Engine**
- **Technology**: OpenAI Whisper (base model)
- **Features**:
  - GPU acceleration support via torch
  - Automatic language detection
  - Timestamp generation
  - Confidence scoring
  - Model caching for performance

### 6. **Speaker Diarization (Optional)**
- **Technology**: pyannote.audio with Hugging Face integration
- **Requirements**: Valid HF_TOKEN and accepted repository terms
- **Features**:
  - Speaker identification and labeling
  - Segment-based speaker assignment
  - Integration with transcription results
  - Fallback to regular transcription if unavailable

### 7. **AI Processing & Summarization**
- **Technology**: xAI Grok API ("grok-beta" model)
- **Features**:
  - Intelligent meeting summarization
  - Action item extraction and structuring
  - Context-aware processing
  - JSON response parsing
  - Error handling for API failures

### 8. **Text-to-Speech Engine**
- **Technology**: pyttsx3 with system TTS engines
- **Features**:
  - Audio feedback for summaries
  - Configurable voice settings
  - Asynchronous processing
  - Accessibility support

## Data Flow Architecture

### Real-Time Audio Processing Flow
```
1. User Speech → Microphone → Web Audio API
2. Audio Processing → Resampling (16kHz) → PCM Encoding
3. Base64 Encoding → WebSocket Transmission
4. Server Reception → Base64 Decoding → Audio Buffer
5. VAD Analysis → Speech/Silence Detection
6. Speech Accumulation → Silence Threshold Check
7. Audio Segmentation → Format Conversion (WAV)
8. Whisper Transcription → Text Generation
9. Speaker Diarization (Optional) → Speaker Labels
10. xAI API Processing → Summarization & Actions
11. Result Formatting → WebSocket Response
12. UI Update → Display Results
```

### Session Management
- **Per-Connection State**: AudioSession class manages individual user sessions
- **Buffer Management**: Separate buffers for incoming audio and accumulated speech
- **State Tracking**: Speech detection, silence counting, processing status
- **Resource Cleanup**: Automatic buffer clearing and session reset

## Technology Stack

### Backend
- **Framework**: FastAPI with WebSocket support
- **Server**: Uvicorn ASGI server
- **Audio Processing**: WebRTC VAD, PyAudio, wave, torchaudio
- **AI/ML**: OpenAI Whisper, pyannote.audio, torch
- **API Integration**: requests, xAI Grok API
- **Data Processing**: pandas, numpy
- **Environment**: python-dotenv, os

### Frontend
- **Core**: HTML5, CSS3, Vanilla JavaScript
- **Audio**: Web Audio API, MediaRecorder API
- **Communication**: WebSocket API
- **UI**: Responsive design with modern CSS

### Development & Deployment
- **Version Control**: Git
- **Environment**: Python virtual environment (.venv)
- **Dependencies**: requirements.txt with pinned versions
- **Configuration**: .env file for API keys
- **Platform**: Ubuntu 24.04.3 LTS (optimized)

## Performance Optimizations

### Caching & Resource Management
- **Model Caching**: Whisper and diarization models cached in memory
- **Connection Pooling**: WebSocket connection management
- **Buffer Optimization**: Efficient audio buffer handling
- **GPU Acceleration**: CUDA support for AI processing

### Error Handling & Resilience
- **Graceful Degradation**: Fallback mechanisms for failed components
- **Timeout Handling**: Configurable timeouts for API calls
- **Resource Cleanup**: Automatic cleanup of temporary files and buffers
- **Logging**: Comprehensive logging for debugging and monitoring

## Scalability Considerations

### Current Limitations
- **Single-User Design**: One session per WebSocket connection
- **Sequential Processing**: Audio segments processed sequentially
- **Memory Usage**: Model loading requires significant RAM
- **Network Dependency**: Requires stable internet for xAI API

### Future Scalability Improvements
- **Multi-User Support**: Session multiplexing and user isolation
- **Concurrent Processing**: Parallel audio processing pipelines
- **Distributed Architecture**: Microservices for different components
- **Load Balancing**: Multiple server instances with load distribution
- **Caching Layer**: Redis for session and result caching

## Security & Privacy

### Data Protection
- **Local Processing**: Audio processed locally when possible
- **API Security**: Secure API key management via environment variables
- **WebSocket Security**: Origin validation and connection limits
- **File Handling**: Secure temporary file creation and cleanup

### Privacy Considerations
- **Audio Data**: Processed in memory, not permanently stored
- **API Communications**: Encrypted HTTPS connections to xAI
- **Local Storage**: Debug files for troubleshooting (can be disabled)
- **User Consent**: Clear microphone permission requests

## Monitoring & Debugging

### Built-in Diagnostics
- **Audio Debugging**: Automatic WAV file generation for troubleshooting
- **VAD Logging**: Real-time speech detection status
- **Performance Metrics**: Processing time and resource usage
- **Error Tracking**: Comprehensive error logging and reporting

### External Monitoring
- **System Resources**: CPU, GPU, and memory usage tracking
- **API Performance**: Response times and success rates
- **WebSocket Health**: Connection status and message throughput
- **User Experience**: UI responsiveness and error rates
