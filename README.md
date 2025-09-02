# Real-Time AI Meeting Assistant

## Overview
This is a FastAPI-based application with WebSocket support that transcribes live audio from your microphone, summarizes meeting content, and extracts action items using the xAI Grok API.

# Real-Time AI Meeting Assistant

## Overview
This is a FastAPI-based application with WebSocket support that provides continuous voice activity detection (VAD), real-time audio transcription, intelligent summarization, and action item extraction using the xAI Grok API.

## Description
The Real-Time AI Meeting Assistant is an advanced FastAPI-based application designed to revolutionize meeting productivity through continuous audio monitoring, intelligent speech detection, and real-time AI processing. Powered by OpenAI Whisper for speech-to-text, WebRTC VAD for voice activity detection, and the xAI Grok API for natural language processing, this tool offers seamless real-time collaboration assistance.

### Key Features

**🎤 Continuous Audio Monitoring**: Advanced Voice Activity Detection (VAD) with automatic speech/silence detection for uninterrupted recording
**📝 Real-Time Transcription**: Live speech-to-text conversion using OpenAI Whisper with optimized performance
**🧠 Intelligent Summarization**: AI-powered meeting summaries using xAI Grok API with contextual understanding
**📋 Action Item Extraction**: Automatic identification and organization of tasks, assignees, and deadlines
**🔊 Audio Feedback**: Text-to-speech summaries for accessibility and hands-free operation
**🌐 Modern Web Interface**: Responsive UI with real-time WebSocket communication
**🎯 Speaker Diarization**: Optional speaker identification using pyannote.audio (requires Hugging Face token)

### Technical Highlights
- **Platform**: Ubuntu 24.04.3 LTS with Python 3.12+
- **Hardware**: Optimized for high-performance systems (Lenovo ThinkPad P16 Gen 2 with NVIDIA RTX 5000)
- **Audio Processing**: WebRTC VAD with configurable sensitivity, 16kHz PCM audio processing
- **Real-Time Communication**: WebSocket-based bidirectional communication
- **AI Stack**: OpenAI Whisper, xAI Grok API, pyannote.audio for diarization
- **Performance**: GPU acceleration support with torch, modular architecture with resource caching

## Features
- **Continuous Recording**: Voice Activity Detection automatically starts/stops recording based on speech detection
- **Real-Time Processing**: Live audio transcription with immediate feedback
- **Smart Segmentation**: Intelligent audio segmentation based on silence detection (configurable 1.5s threshold)
- **Multi-Format Support**: Handles WebM, WAV, and raw PCM audio formats
- **Error Handling**: Comprehensive error handling with fallback mechanisms
- **Debug Support**: Built-in audio debugging with file generation for troubleshooting
- **Cross-Browser Compatibility**: Works with modern browsers supporting Web Audio API and MediaRecorder

## Installation
1. Clone the repository: `git clone https://github.com/dentity007/realtime-ai-assistant.git`
2. Navigate: `cd realtime-ai-assistant`
3. Create virtual environment: `python3 -m venv .venv`
4. Activate: `source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Configure API keys: Create `.env` with required API keys

## Configuration
Create a `.env` file in the project root:
```bash
# Required: xAI Grok API Key
XAI_API_KEY=your-xai-api-key-here

# Optional: Hugging Face Token for speaker diarization
HF_TOKEN=your-huggingface-token-here
```

## Usage
1. **Start the server**: `python app.py`
2. **Open browser**: Navigate to `http://localhost:8000`
3. **Test microphone**: Click "Test Microphone" to verify audio access
4. **Start recording**: Click "Start Continuous Recording"
5. **Speak naturally**: The system automatically detects speech and processes audio segments
6. **View results**: Transcriptions, summaries, and action items appear in real-time

## VAD Configuration
The Voice Activity Detection can be tuned via constants in `app.py`:
- `VAD_AGGRESSIVENESS`: Sensitivity level (0-3, default: 1)
- `SILENCE_THRESHOLD`: Frames of silence before processing (default: 50 = 1.5s)
- `FRAME_DURATION`: Audio frame size in ms (default: 30ms)

## Recent Updates
- ✅ Implemented advanced Voice Activity Detection (VAD) for continuous recording
- ✅ Added real-time WebSocket communication for live audio processing
- ✅ Enhanced audio processing with proper speech buffer management
- ✅ Improved frontend with Web Audio API integration
- ✅ Added comprehensive debugging and error handling
- ✅ Optimized performance with GPU acceleration support
- ✅ Fixed audio format handling and conversion issues

## API Endpoints
- `GET /`: Main web interface
- `WebSocket /ws`: Real-time audio processing endpoint
- Static files served from `/static/`

## Troubleshooting
- **Microphone Issues**: Ensure browser permissions and check audio devices
- **VAD Problems**: Adjust `VAD_AGGRESSIVENESS` (lower = more sensitive)
- **Transcription Errors**: Check audio quality and Whisper model loading
- **WebSocket Issues**: Verify server is running on correct port (8000)

## Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test thoroughly
4. Submit a pull request with detailed description

## License
MIT License - See LICENSE file for details

## Documentation

For detailed information about the project, see the following documentation files:

- **[Setup Guide](docs/Setup%20Guide%20for%20Real%20Time.md)**: Complete installation and setup instructions
- **[Architecture](docs/architecture.md)**: System architecture and technical details
- **[API Documentation](docs/api.md)**: WebSocket API reference and message formats
- **[Configuration Guide](CONFIG.md)**: All configurable parameters and settings
- **[Changelog](CHANGELOG.md)**: Version history and feature updates
- **[Troubleshooting](TROUBLESHOOTING.md)**: Common issues and solutions

## Quick Configuration

Create a `.env` file in the project root:
```bash
# Required: xAI Grok API Key
XAI_API_KEY=your-xai-api-key-here

# Optional: Hugging Face Token for speaker diarization
HF_TOKEN=your-huggingface-token-here
```

## Future Enhancements
- Multi-speaker support with improved diarization
- Meeting recording with timestamp indexing
- Integration with calendar applications
- Mobile app companion
- Advanced noise reduction and echo cancellation
Key Features

Live Audio Transcription: Captures and transcribes 5-second audio clips from your microphone using the Whisper model, optimized for GPU acceleration on compatible hardware.
Intelligent Summarization: Utilizes the xAI Grok API to distill meeting discussions into concise summaries, enhancing comprehension and retention.
Action Item Extraction: Automatically identifies and organizes tasks, assignees, and due dates, presented in an interactive table for easy tracking.
Text-to-Speech Feedback: Provides audible summaries via pyttsx3, ensuring accessibility and hands-free operation.
User-Friendly Interface: Built with FastAPI and WebSockets, offering a responsive web-based UI accessible at http://localhost:8000.

Technical Highlights
Developed on Ubuntu 24.04.3 LTS, the application harnesses a robust tech stack including PyAudio for audio capture, pandas for data management, and torch for GPU support. It’s designed to run efficiently on high-performance systems like the Lenovo ThinkPad P16 Gen 2, utilizing its NVIDIA RTX 5000 for accelerated processing. The code is modular, with cached resources to optimize performance, and includes comprehensive error handling for a reliable user experience.
Getting Started
Clone the repository, set up your environment with the provided requirements.txt, and configure your xAI API key to begin. The app is ready for local deployment, with detailed setup instructions in docs/Setup Guide for Real Time.md. Whether for personal use or team collaboration, this assistant adapts to your meeting needs, making it a versatile tool for the modern workplace.
Future Potential
Planned enhancements include live audio streaming for continuous transcription, multi-user support, and advanced features like improved speaker identification. Contributions are welcome to expand its capabilities and reach.

## Features
- Records 5-second audio clips from your microphone via web interface.
- Transcribes audio using the Whisper model.
- Performs speaker diarization to distinguish between speakers (requires Hugging Face token).
- Queries the xAI Grok API for summaries and action items.
- Provides text-to-speech feedback.
- Real-time communication via WebSockets.

## Installation
1. Clone the repository: `git clone https://github.com/yourusername/realtime-ai-assistant.git`
2. Navigate: `cd realtime-ai-assistant`
3. Create venv: `python3 -m venv venv`
4. Activate: `source venv/bin/activate`
5. Install: `pip install -r requirements.txt`
6. Set API keys: Create `.env` with `XAI_API_KEY=your-api-key` and optionally `HF_TOKEN=your-huggingface-token` for speaker diarization.

## Usage
- Run: `python app.py` or `uvicorn app:app --reload`
- Open browser to http://localhost:8000
- Click "Record & Analyze" to record and see results.

## Recent Updates
- Converted from Streamlit to FastAPI with WebSocket support.
- Added web-based UI with real-time audio recording.
- Enhanced real-time communication.

## Contributing
- Fork and create a feature branch.
- Commit and open a pull request.

## License
[MIT] - Consult legal.

## Additional Setup
See [docs/setup.md](docs/setup.md).
