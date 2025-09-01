# Architecture of Real-Time AI Meeting Assistant

## System Overview
The Real-Time AI Meeting Assistant is a Streamlit application designed to transcribe audio, summarize meetings, and extract action items using the xAI Grok API.

## Components
- **User Interface**: Built with Streamlit, providing a web-based interface for recording and viewing results.
- **Audio Capture**: Uses PyAudio to record 5-second audio clips from the default microphone, saved as a temporary WAV file.
- **Transcription**: Employs the Whisper model (cached with `@st.cache_resource`) to convert audio to text, optimized for GPU if available.
- **LLM Processing**: Queries the xAI Grok API ("grok-3" model) with a structured prompt to generate JSON responses containing summaries and actions.
- **Text-to-Speech**: Utilizes pyttsx3 to provide audible feedback.
- **Data Storage**: Maintains session state with a summary string and an actions DataFrame.

## Data Flow
1. User clicks "Record & Analyze" to start a 5-second recording.
2. PyAudio captures audio and saves it to `temp_audio.wav`.
3. Whisper transcribes the audio into text.
4. The text is sent to the xAI API via a POST request.
5. The API response (JSON) is parsed and used to update the UI and speak the summary.
6. Actions are stored in a DataFrame for display.

## Technology Stack
- **Frontend**: Streamlit
- **Audio**: PyAudio, wave
- **AI**: Whisper (via openai-whisper), xAI Grok API
- **TTS**: pyttsx3
- **Data**: pandas, numpy
- **Environment**: Python 3.10+, torch (for GPU)

## Scalability and Limitations
- Current design is single-user and sequential, limiting real-time performance.
- Future enhancements could include live streaming and multi-user support.
