# Spanish to English Voice Translation Example

This is an example project demonstrating real-time Spanish to English voice translation using:
- 🎤 Vosk for speech recognition
- 🌍 Argos Translate for translation
- 🔊 Coqui TTS for text-to-speech

It serves as a reference implementation for building voice translation applications with these technologies.

## 🚀 Example Scripts (Incremental Integration)

### 1. `main-vosk.py` - Basic Speech Recognition
- 🎤 Real-time Spanish speech recognition using Vosk
- 🎧 Continuous listening mode
- ℹ️ Shows recognized Spanish text

### 2. `main-vosk-argos.py` - Add Translation
- ✅ All features from `main-vosk.py`
- ➕ Adds real-time translation using Argos Translate
- 🌍 Displays both original Spanish and English translation
- 📝 Shows partial recognition results

### 3. `main-vosk-argos-tts.py` - Add Text-to-Speech
- ✅ All features from `main-vosk-argos.py`
- ➕ Adds text-to-speech using Coqui TTS
- 🔊 Speaks the English translation aloud
- 🎛️ Full voice-to-voice translation pipeline

## 🛠️ Prerequisites

- Python 3.11+
- [UV](https://github.com/astral-sh/uv) (Ultra-fast Python package installer)
- PortAudio (required for PyAudio)
  ```bash
  # Install UV (if not already installed)
  curl -sSf https://astral.sh/uv/install.sh | sh
  
  # Install PortAudio on macOS
  brew install portaudio
  ```

## 🏗️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/voice-translate.git
   cd voice-translate
   ```

2. **Install dependencies using UV**
   ```bash
   # Create and activate a virtual environment (optional but recommended)
   uv venv

   # Install all dependencies from pyproject.toml
   uv sync # On MacOS: uv sync --extra macos
   
   # Activate the virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Vosk Spanish Model**
   ```bash
   # Create model directory
   mkdir -p model

   # Download and extract the Spanish model (small version ~50MB)
   curl -L https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip -o vosk-model-es.zip
   unzip vosk-model-es.zip -d model_temp
   mv model_temp/vosk-model-small-es-0.42/* model/
   
   # Clean up
   rm -rf model_temp vosk-model-es.zip
   ```

   For better accuracy (but larger download ~1.8GB), use the full model:
   ```bash
   curl -L https://alphancephei.com/vosk/models/vosk-model-es-0.42.zip -o vosk-model-es.zip
   unzip vosk-model-es.zip -d model_temp
   mv model_temp/vosk-model-es-0.42/* model/
   rm -rf model_temp vosk-model-es.zip
   ```

## 🚀 Usage

### 1. Basic Speech Recognition
```bash
python main-vosk.py
```
- Speak in Spanish when prompted
- See the recognized Spanish text
- Press `Ctrl+C` to stop

### 2. Add Translation
```bash
python main-vosk-argos.py
```
- Automatically downloads Argos Translate model on first run
- Speak in Spanish
- See both original Spanish and English translation
- Press `Ctrl+C` to stop

### 3. Add Text-to-Speech
```bash
python main-vosk-argos-tts.py
```
- First run will download required models (may take time)
- Speak in Spanish
- Hear the English translation spoken aloud
- See both original and translated text
- Press `Ctrl+C` to stop

## 📝 License

This project is licensed under the MIT License.
