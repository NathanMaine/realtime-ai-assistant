# Setup Guide for Real-Time AI Meeting Assistant

## Hardware Requirements
- Lenovo ThinkPad P16 Gen 2 or similar with a microphone.
- GPU (e.g., NVIDIA RTX 5000) enhances performance.

## Software Requirements
- Ubuntu 24.04.3 LTS.
- Python 3.10+.
- Dependencies in `requirements.txt`.

## Installation Steps
1. Update: `sudo apt update && sudo apt upgrade`
2. Install tools: `sudo apt install python3-dev python3-pip portaudio19-dev`
3. Follow `README.md` installation.
4. Configure audio: Check groups, test with `arecord`.
5. API key: From https://console.x.ai.

## Troubleshooting
- ALSA errors: `pkill -9 arecord; pulseaudio -k && pulseaudio --start`
- PyAudio: `pip install pyaudio==0.2.14`
- GPU: `nvidia-smi; python -c "import torch; print(torch.cuda.is_available())"`

## Known Issues
- Device index may need adjustment.
- LLM format depends on API.

## Contact
- Via GitHub Issues.
