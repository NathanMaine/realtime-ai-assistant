# Setup Guide for Real-Time AI Meeting Assistant

## System Requirements

### Hardware Requirements
- **CPU**: Multi-core processor (recommended: 4+ cores)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB free space for models and temporary files
- **GPU**: NVIDIA GPU with CUDA support (optional, recommended for better performance)
- **Microphone**: Any standard microphone or built-in laptop microphone
- **Network**: Stable internet connection for xAI API access

### Software Requirements
- **Operating System**: Ubuntu 24.04.3 LTS (or compatible Linux distribution)
- **Python**: Python 3.12+ (tested on 3.12.3)
- **Browser**: Modern browser with Web Audio API support (Chrome 88+, Firefox 85+, Edge 88+, Safari 14+)
- **Audio System**: ALSA/PulseAudio for Linux audio

## Installation Steps

### 1. System Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-dev python3-pip python3-venv
sudo apt install -y portaudio19-dev ffmpeg
sudo apt install -y libsndfile1 libsndfile1-dev

# Install CUDA (optional, for GPU acceleration)
# Follow NVIDIA CUDA installation guide for your GPU
```

### 2. Repository Setup
```bash
# Clone the repository
git clone https://github.com/dentity007/realtime-ai-assistant.git
cd realtime-ai-assistant

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Dependencies Installation
```bash
# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installations
python -c "import torch; print('PyTorch version:', torch.__version__)"
python -c "import whisper; print('Whisper available')"
python -c "import webrtcvad; print('WebRTC VAD available')"
```

### 4. Audio System Configuration
```bash
# Check audio devices
arecord -l
aplay -l

# Test microphone (adjust device index if needed)
arecord -d 5 -f cd test.wav
aplay test.wav

# Check PulseAudio (if using)
pulseaudio --check
pulseaudio --start
```

## API Configuration

### Required: xAI API Key
1. Visit [https://console.x.ai](https://console.x.ai)
2. Sign up for an account
3. Generate an API key
4. Add to `.env` file:
```bash
XAI_API_KEY=xai-your-api-key-here
```

### Optional: Hugging Face Token (for Speaker Diarization)
1. Visit [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create a new token with "Read" permissions
3. Visit [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
4. Accept the repository terms
5. Add to `.env` file:
```bash
HF_TOKEN=hf_your-huggingface-token-here
```

## Environment Configuration

Create a `.env` file in the project root:
```bash
# Required API Keys
XAI_API_KEY=xai-your-api-key-here

# Optional: Speaker Diarization
HF_TOKEN=hf_your-huggingface-token-here

# Optional: VAD Tuning (advanced users)
# VAD_AGGRESSIVENESS=1  # 0-3 (lower = more sensitive)
# SILENCE_THRESHOLD=50  # frames (50 = 1.5 seconds)
```

## VAD (Voice Activity Detection) Configuration

The system uses WebRTC VAD for automatic speech detection. You can tune these parameters:

### VAD_AGGRESSIVENESS (0-3)
- **0**: Most sensitive (detects more speech, may include noise)
- **1**: Balanced (recommended, current default)
- **2**: Less sensitive (fewer false positives)
- **3**: Least sensitive (only clear speech)

### SILENCE_THRESHOLD
- **Lower values** (20-30): Faster processing, shorter segments
- **Higher values** (40-60): Slower processing, longer segments
- **Current default**: 50 frames = 1.5 seconds of silence

### FRAME_DURATION
- **10ms**: More responsive, higher CPU usage
- **20ms**: Balanced performance
- **30ms**: Smoother processing, current default

## Running the Application

### Basic Startup
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the server
python app.py
```

### Advanced Options
```bash
# Run with custom host/port
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Run in background
nohup python app.py &

# Check if running
ps aux | grep python
```

### Accessing the Application
1. Open browser to `http://localhost:8000`
2. Click "Test Microphone" to verify audio access
3. Click "Start Continuous Recording"
4. Speak and observe real-time processing

## Troubleshooting Guide

### Audio/Microphone Issues

**Microphone Not Detected**
```bash
# Check audio devices
arecord -l

# Test recording
arecord -d 3 -f cd test.wav

# Check permissions
groups $USER  # Should include 'audio' group
```

**Browser Microphone Permission Denied**
- Ensure HTTPS or localhost access
- Check browser settings for microphone permissions
- Try refreshing the page and re-granting permissions

**Audio Quality Issues**
- Check microphone placement and background noise
- Test with different microphones
- Verify sample rate (16kHz required)

### VAD (Voice Activity Detection) Issues

**"No speech detected" errors**
- Lower `VAD_AGGRESSIVENESS` (try 0)
- Check microphone input levels
- Reduce background noise

**Recording stops too early**
- Increase `SILENCE_THRESHOLD` (try 60-70)
- Check for consistent audio input

**Recording doesn't start**
- Verify microphone permissions in browser
- Check WebSocket connection
- Look for JavaScript console errors

### Performance Issues

**High CPU Usage**
- Enable GPU acceleration if available
- Reduce `FRAME_DURATION` to 20ms
- Close other applications

**Slow Transcription**
- Ensure GPU is available: `nvidia-smi`
- Check PyTorch CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
- Use smaller Whisper model if needed

**Memory Issues**
- Monitor RAM usage during operation
- Close other memory-intensive applications
- Consider using smaller AI models

### API and Network Issues

**xAI API Errors**
- Verify `XAI_API_KEY` in `.env`
- Check internet connection
- Monitor API rate limits

**WebSocket Connection Failed**
- Ensure server is running on port 8000
- Check firewall settings
- Verify no port conflicts

**Speaker Diarization Fails**
- Verify `HF_TOKEN` validity
- Confirm Hugging Face terms acceptance
- Check internet connection for model downloads

### Debug Mode

Enable detailed logging:
```bash
# Check server logs for detailed output
python app.py 2>&1 | tee debug.log

# Examine debug audio files
ls -la debug_audio_*.wav
sox debug_audio_*.wav -n stat  # Analyze audio properties
```

## Advanced Configuration

### Custom VAD Settings
Edit `app.py` to modify VAD parameters:
```python
# VAD settings
VAD_AGGRESSIVENESS = 1  # Adjust sensitivity
SILENCE_THRESHOLD = 50  # Adjust silence duration
FRAME_DURATION = 30  # Adjust frame size
```

### GPU Optimization
```python
# Force GPU usage
import torch
torch.cuda.set_device(0)  # Use specific GPU
```

### Audio Format Tuning
- **Sample Rate**: Fixed at 16kHz for Whisper compatibility
- **Channels**: Mono (single channel)
- **Bit Depth**: 16-bit PCM
- **Format**: WAV (converted from WebM/PCM as needed)

## Security Considerations

### API Key Security
- Never commit `.env` file to version control
- Use strong, unique API keys
- Rotate keys periodically
- Limit API key permissions

### Network Security
- Run on localhost for development
- Use HTTPS in production
- Implement rate limiting for API calls
- Monitor for unusual activity

### Data Privacy
- Audio processed locally when possible
- Debug files contain sensitive audio data
- Clear temporary files regularly
- Implement data retention policies

## Performance Tuning

### For High-Performance Systems
- Use GPU acceleration
- Increase buffer sizes
- Optimize VAD parameters for your environment
- Monitor system resources

### For Low-Resource Systems
- Use CPU-only mode
- Reduce VAD sensitivity
- Increase silence thresholds
- Use smaller Whisper models

## Support and Community

### Getting Help
- Check the troubleshooting section above
- Review server logs for error messages
- Test with different browsers and microphones
- Verify all dependencies are correctly installed

### Contributing
- Report issues on GitHub
- Suggest improvements and features
- Submit pull requests for bug fixes
- Share performance optimizations

### Known Limitations
- Single-user design (one session per browser tab)
- Requires stable internet for xAI API
- GPU memory requirements for optimal performance
- Browser-dependent audio API support

---

**Last Updated**: September 1, 2025
**Version**: 4.0
**Tested On**: Ubuntu 24.04.3 LTS, Python 3.12.3
