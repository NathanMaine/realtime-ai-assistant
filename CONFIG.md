# Configuration Guide - Real-Time AI Meeting Assistant

## Overview
This document outlines the configurable parameters for the Real-Time AI Meeting Assistant, including VAD settings, audio processing parameters, and API configurations.

## VAD (Voice Activity Detection) Configuration

### Core Parameters
```python
# VAD Sensitivity (0-3, where 0 is most sensitive)
VAD_AGGRESSIVENESS = 1  # Recommended: 1 (balanced)

# Silence Threshold (frames, 1 frame = 30ms)
SILENCE_THRESHOLD = 50  # 50 frames = 1.5 seconds

# Minimum Speech Duration (frames)
MIN_SPEECH_DURATION = 10  # 10 frames = 300ms minimum
```

### VAD Sensitivity Levels
- **0**: Most sensitive - catches more speech but may include noise
- **1**: Balanced - recommended for most use cases
- **2**: Less sensitive - reduces false positives
- **3**: Most conservative - only detects very clear speech

### Audio Processing Parameters
```python
# Audio Format Settings
SAMPLE_RATE = 16000  # 16kHz (Whisper requirement)
CHANNELS = 1  # Mono
SAMPLE_WIDTH = 2  # 16-bit

# Buffer Settings
AUDIO_BUFFER_SIZE = 1024  # Web Audio API buffer size
SPEECH_BUFFER_SIZE = 16000  # ~1 second at 16kHz

# Processing Settings
MAX_AUDIO_LENGTH = 30  # Maximum segment length in seconds
MIN_AUDIO_LENGTH = 1   # Minimum segment length in seconds
```

## API Configuration

### OpenAI Whisper
```python
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
WHISPER_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
WHISPER_LANGUAGE = "en"  # Auto-detect if None
```

### xAI Grok API
```python
XAI_API_KEY = os.getenv("XAI_API_KEY")
XAI_MODEL = "grok-beta"
XAI_MAX_TOKENS = 1000
XAI_TEMPERATURE = 0.7
```

### Optional: Speaker Diarization
```python
DIARIZATION_ENABLED = True
DIARIZATION_MODEL = "pyannote/speaker-diarization-3.1"
DIARIZATION_AUTH_TOKEN = os.getenv("HF_AUTH_TOKEN")
```

## WebSocket Configuration

### Connection Settings
```python
WEBSOCKET_MAX_SIZE = 1024 * 1024 * 10  # 10MB max message
WEBSOCKET_PING_INTERVAL = 30  # seconds
WEBSOCKET_PING_TIMEOUT = 10  # seconds
```

### Message Types
- `audio_data`: Base64-encoded PCM audio
- `start_recording`: Begin audio capture
- `stop_recording`: End audio capture
- `vad_status`: VAD detection updates
- `transcription`: Speech-to-text results
- `summary`: AI-generated meeting summary
- `error`: Error messages

## Server Configuration

### FastAPI Settings
```python
HOST = "0.0.0.0"
PORT = 8000
RELOAD = True  # Development mode
WORKERS = 1    # Single worker for audio processing
```

### CORS Settings
```python
ALLOWED_ORIGINS = ["*"]  # Configure for production
ALLOWED_METHODS = ["GET", "POST", "OPTIONS"]
ALLOWED_HEADERS = ["*"]
```

## Debug and Logging

### Debug Settings
```python
DEBUG_MODE = True
DEBUG_AUDIO_SAVE = True  # Save debug audio files
DEBUG_VAD_LOG = True    # Log VAD decisions
```

### Log Configuration
```python
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "app.log"
```

## Performance Tuning

### GPU Settings
```python
# PyTorch GPU settings
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.enabled = True

# Memory management
PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:512"
```

### Audio Processing Optimization
```python
# Buffer pre-allocation
PREALLOCATE_BUFFERS = True
BUFFER_POOL_SIZE = 10

# Async processing
MAX_CONCURRENT_TRANSCRIPTIONS = 2
PROCESSING_QUEUE_SIZE = 100
```

## Environment Variables

### Required
```bash
XAI_API_KEY=your_xai_api_key_here
HF_AUTH_TOKEN=your_huggingface_token_here  # Optional, for diarization
```

### Optional
```bash
CUDA_VISIBLE_DEVICES=0  # GPU device selection
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

## Troubleshooting

### Common VAD Issues
- **No speech detected**: Reduce VAD_AGGRESSIVENESS (try 0)
- **Too many false positives**: Increase VAD_AGGRESSIVENESS (try 2-3)
- **Short segments**: Increase SILENCE_THRESHOLD
- **Long segments**: Decrease SILENCE_THRESHOLD

### Audio Quality Issues
- **Poor transcription**: Ensure 16kHz sample rate
- **Noise interference**: Adjust microphone settings
- **Format errors**: Check Web Audio API compatibility

### Performance Issues
- **High CPU usage**: Enable GPU acceleration
- **Memory leaks**: Monitor buffer sizes
- **Slow processing**: Reduce model size or optimize settings

---

**Note**: These settings are optimized for the current implementation. Adjust based on your specific hardware and use case requirements.
