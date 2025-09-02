# Troubleshooting Guide - Real-Time AI Meeting Assistant

## Quick Start Checklist

### Before Running
- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] xAI API key set (`export XAI_API_KEY=your_key`)
- [ ] Microphone permissions granted in browser
- [ ] Port 8000 available

### Basic Test
```bash
# Test server startup
python app.py

# Check browser console for errors
# Verify microphone access prompt appears
```

## Common Issues and Solutions

### 1. "No speech detected" Error

**Symptoms:**
- VAD not detecting any speech
- Audio segments are very short (< 0.1s)
- Transcription fails with empty results

**Solutions:**
```python
# In app.py, adjust VAD settings:
VAD_AGGRESSIVENESS = 0  # Most sensitive (try 0-1)
SILENCE_THRESHOLD = 30  # Shorter silence detection
```

**Additional Steps:**
- Check microphone input levels
- Test with different browsers
- Verify audio format (16kHz, mono, 16-bit PCM)

### 2. WebSocket Connection Issues

**Symptoms:**
- "WebSocket connection failed" in browser console
- No real-time updates
- Server shows connection errors

**Solutions:**
- Check server is running on correct port (8000)
- Verify CORS settings in FastAPI
- Test with different browsers
- Check firewall settings
- Try incognito mode (disable extensions)

**Debug Command:**
```bash
# Check if port is in use
netstat -tlnp | grep :8000

# Test WebSocket connection manually
curl -I http://localhost:8000
```

### 3. Audio Quality Problems

**Symptoms:**
- Poor transcription accuracy
- Background noise interference
- Echo or distortion

**Solutions:**
- Use external microphone instead of built-in
- Reduce background noise
- Adjust microphone sensitivity in OS settings
- Test in quiet environment
- Check sample rate (must be 16kHz)

### 4. GPU/Performance Issues

**Symptoms:**
- Slow processing times
- High CPU usage
- Out of memory errors

**Solutions:**
```python
# Force CPU if GPU issues
WHISPER_DEVICE = "cpu"

# Reduce model size
WHISPER_MODEL = "tiny"  # Instead of "base"
```

**Hardware Requirements:**
- Minimum: 4GB RAM, dual-core CPU
- Recommended: 8GB RAM, quad-core CPU, GPU
- Optimal: 16GB RAM, modern GPU with CUDA

### 5. Browser Compatibility Issues

**Supported Browsers:**
- ✅ Chrome 88+
- ✅ Firefox 85+
- ✅ Safari 14+
- ✅ Edge 88+

**Common Fixes:**
- Update browser to latest version
- Enable microphone permissions
- Disable browser extensions temporarily
- Try incognito/private mode

### 6. API Key Issues

**Symptoms:**
- "Invalid API key" errors
- xAI API calls failing
- No summaries generated

**Solutions:**
```bash
# Set environment variable
export XAI_API_KEY="your_actual_key_here"

# Verify key format (should start with 'xai-')
echo $XAI_API_KEY

# Test API key
curl -H "Authorization: Bearer $XAI_API_KEY" \
     https://api.x.ai/v1/models
```

### 7. Import/Dependency Errors

**Symptoms:**
- Module not found errors
- Import failures on startup

**Solutions:**
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+

# Virtual environment issues
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 8. Audio Format Errors

**Symptoms:**
- "Invalid audio format" messages
- WebRTC errors in console

**Solutions:**
- Ensure audio is 16kHz, mono, 16-bit PCM
- Check Web Audio API support
- Verify MediaRecorder compatibility
- Test with different audio devices

## Debug Mode

### Enable Debug Logging
```python
# In app.py
DEBUG_MODE = True
DEBUG_AUDIO_SAVE = True
DEBUG_VAD_LOG = True
```

### Debug Files Generated
- `debug_audio_*.wav`: Raw audio segments
- `vad_log.txt`: VAD decision log
- `app.log`: Application logs

### Analyzing Debug Output
```bash
# Check VAD decisions
tail -f vad_log.txt

# Listen to debug audio
aplay debug_audio_001.wav

# Monitor server logs
tail -f app.log
```

## Performance Monitoring

### Key Metrics to Monitor
- Audio segment length (should be 2-5+ seconds)
- Processing time per segment (< 2 seconds)
- Memory usage (should not exceed system RAM)
- WebSocket latency (< 100ms)

### Optimization Tips
- Use GPU for Whisper if available
- Reduce model size for faster processing
- Increase buffer sizes for smoother operation
- Monitor system resources during use

## Advanced Troubleshooting

### Network Issues
```bash
# Test connectivity
ping api.x.ai

# Check DNS resolution
nslookup api.x.ai

# Test with different network
# (Try mobile hotspot if WiFi issues)
```

### Audio Device Issues
```bash
# List audio devices (Linux)
arecord -l

# Test audio input
arecord -d 5 test.wav
aplay test.wav
```

### Memory Leaks
- Monitor Python process memory usage
- Check for buffer accumulation
- Restart server periodically
- Update to latest PyTorch version

## Getting Help

### Debug Information to Provide
1. **System Info:**
   - OS version
   - Python version
   - Browser version
   - Hardware specs

2. **Error Logs:**
   - Browser console errors
   - Server logs (`app.log`)
   - VAD debug logs

3. **Configuration:**
   - Current VAD settings
   - API keys (masked)
   - Audio device info

### Test Commands
```bash
# Full system test
python -c "
import sys
print('Python version:', sys.version)
import torch
print('PyTorch CUDA available:', torch.cuda.is_available())
import whisper
print('Whisper available')
import webrtcvad
print('WebRTC VAD available')
"
```

---

**Last Updated**: September 1, 2025
**Version**: 4.0
