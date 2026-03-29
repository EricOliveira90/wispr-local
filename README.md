# Whisper Local — Faster-Whisper Test

A simple test script for [faster-whisper](https://github.com/SYSTRAN/faster-whisper) speech-to-text on Windows. CPU-only, no cloud/API keys needed.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the test

```bash
# Record 5 seconds of audio and transcribe (English, base model)
python test_whisper.py

# Record in Portuguese
python test_whisper.py --lang pt

# Use a different model size
python test_whisper.py --model tiny      # Fastest, least accurate
python test_whisper.py --model turbo     # Best speed/accuracy tradeoff

# Record for longer
python test_whisper.py --duration 10

# Transcribe an existing audio file
python test_whisper.py --file recording.wav

# Auto-detect language
python test_whisper.py --lang auto

# Save the recording as a WAV file
python test_whisper.py --save

# List available microphone devices
python test_whisper.py --list-devices

# Use a specific microphone
python test_whisper.py --device 1
```

## Model Sizes

| Model   | Size   | Speed  | Accuracy | First Download |
|---------|--------|--------|----------|----------------|
| `tiny`  | ~75 MB | ⚡⚡⚡⚡ | ★☆☆☆     | ~30s           |
| `base`  | ~150 MB| ⚡⚡⚡  | ★★☆☆     | ~1min          |
| `small` | ~500 MB| ⚡⚡   | ★★★☆     | ~2min          |
| `medium`| ~1.5 GB| ⚡     | ★★★★     | ~5min          |
| `turbo` | ~1.5 GB| ⚡⚡⚡  | ★★★★     | ~5min          |
| `large-v3`| ~3 GB| ⚡    | ★★★★★    | ~10min         |

> **Note:** Models are downloaded automatically on first use and cached locally (~`%USERPROFILE%\.cache\huggingface`).

## Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--model` | `-m` | Model size (tiny/base/small/medium/turbo/large-v3) | `base` |
| `--lang` | `-l` | Language code (en, pt, es, fr...) or `auto` | `en` |
| `--duration` | `-d` | Recording duration in seconds | `5` |
| `--file` | `-f` | Audio file path (skips mic recording) | — |
| `--beam-size` | `-b` | Beam size for decoding | `5` |
| `--device` | | Audio input device index | default mic |
| `--list-devices` | | List audio input devices | — |
| `--save` | `-s` | Save recording as WAV | — |

## Requirements

- Windows 10/11
- Python 3.9+
- Microphone (for live recording)
- ~150 MB–3 GB disk space (depending on model, downloaded on first run)
- No internet needed after initial model download
