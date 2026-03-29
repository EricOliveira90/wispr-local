# Whisper Local — Privacy-First Speech-to-Text for Windows

A local, CPU-only speech-to-text application for Windows that types transcribed speech into any focused app. No cloud, no API keys — fully offline after initial model download.

## Features

- **Global hotkey dictation** — Ctrl+Win for English, Alt+Win for Portuguese
- **System tray icon** with color-coded states (Gray=Idle, Yellow=Loading, Dark Blue=Ready, Bright Blue=Listening EN, Green=Listening PT)
- **Three output modes** — Type to field (simulated keystrokes), Clipboard only, or Both
- **Smart resource management** — Model loads on demand, auto-stops after 30s silence, auto-unloads after 10min idle
- **Toast notifications** on model load/unload events
- **Persistent settings** via `settings.json` — model size, output mode, run-on-startup
- **Run on startup** — registry-based (HKCU), no admin needed
- **Powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper)** with int8 CPU inference and VAD filtering

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch the app

There are several ways to start Whisper Local. All of them make the app appear as a **system tray icon** (near the clock).

#### Option A: Double-click `launch.cmd` (recommended)

Double-click **`launch.cmd`** in File Explorer. A CMD window flashes briefly and closes — the app starts silently in the system tray.

#### Option B: From PowerShell or CMD

```powershell
# From PowerShell:
.\launch.cmd

# Or explicitly call wscript:
wscript .\launch.vbs
```

#### Option C: Debug mode (console stays open)

```bash
python -m whisper_local.app
```

Use this if you want to see console output for debugging.

> **Troubleshooting:** If double-clicking `launch.vbs` opens it in Notepad instead of running it, your `.vbs` file association may be misconfigured. Use `launch.cmd` instead, or run `wscript .\launch.vbs` from a terminal.

### 3. Use it

1. The tray icon appears (Gray = idle, no model loaded)
2. Press **Ctrl+Win** to start English dictation (model loads on first use)
3. Speak into your microphone — text appears in the focused field
4. Press **Ctrl+Win** again to stop, or wait 30s of silence for auto-stop
5. After 10 minutes idle, the model auto-unloads to free RAM

### 4. Run on Windows startup (optional)

To have Whisper Local start automatically when you log in:

1. Right-click the tray icon
2. Check **"Run on Startup"**

This adds a registry entry under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` that launches the app silently via `wscript.exe launch.vbs`. No admin rights needed. Uncheck the option to remove it.

## Hotkeys

| Hotkey | Action |
|--------|--------|
| **Ctrl+Win** | Toggle English dictation |
| **Alt+Win** | Toggle Portuguese dictation |
| **Ctrl+Shift+Q** | Quit the application |

Pressing one language hotkey while the other is active switches language seamlessly.

## Tray Menu

Right-click the tray icon for:

- **Load Model** / **Unload Model** — manual model lifecycle control
- **Output Mode** — Type to field / Clipboard only / Both
- **Model Size** — Tiny / Base / Small / Turbo (only changeable when model is unloaded)
- **Run on Startup** — toggle Windows auto-start
- **Quit** — exit the application

## Tray Icon States

| Color | State |
|-------|-------|
| Gray | Idle (no model loaded) |
| Yellow | Loading model... |
| Dark Blue | Ready (model loaded, not listening) |
| Bright Blue | Listening (English) |
| Green | Listening (Portuguese) |

## Model Sizes

| Model | Size | Speed | Accuracy | First Download |
|-------|------|-------|----------|----------------|
| `tiny` | ~75 MB | ⚡⚡⚡⚡ | ★☆☆☆ | ~30s |
| `base` | ~150 MB | ⚡⚡⚡ | ★★☆☆ | ~1min |
| `small` | ~500 MB | ⚡⚡ | ★★★☆ | ~2min |
| `turbo` | ~1.5 GB | ⚡⚡⚡ | ★★★★ | ~5min |

> **Default: Turbo** — best speed/accuracy tradeoff. Models are downloaded automatically on first use and cached locally (~`%USERPROFILE%\.cache\huggingface`).

## Settings

Settings are persisted in `settings.json` (created automatically on first run):

```json
{
  "model_size": "turbo",
  "output_mode": "type",
  "run_on_startup": false
}
```

| Setting | Values | Default | Notes |
|---------|--------|---------|-------|
| `model_size` | tiny, base, small, turbo | turbo | Only changeable when model is unloaded |
| `output_mode` | type, clipboard, both | type | Takes effect immediately |
| `run_on_startup` | true, false | false | Uses HKCU registry, no admin needed |

## Architecture

```
whisper_local/
├── app.py        — Main orchestrator (wires all subsystems)
├── engine.py     — Transcription engine (faster-whisper wrapper)
├── audio.py      — Microphone capture (sounddevice)
├── tray.py       — System tray icon (pystray + Pillow)
├── hotkeys.py    — Global hotkey registration (keyboard)
├── output.py     — Text delivery (pyautogui + pyperclip)
└── settings.py   — Settings persistence (JSON + registry)
```

## Testing

The project includes 30 integration-style tests covering all major behaviors:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_app.py -v
python -m pytest tests/test_engine.py -v
python -m pytest tests/test_output.py -v
python -m pytest tests/test_settings.py -v
python -m pytest tests/test_timers.py -v
```

## Requirements

- Windows 10/11
- Python 3.9+
- Microphone
- ~150 MB–1.5 GB disk space (depending on model, downloaded on first run)
- No internet needed after initial model download
- No admin rights required

## Typical Flow

1. Launch via `launch.bat` or auto-start → tray icon appears (Gray)
2. Focus a text field → press Ctrl+Win → speak → text appears
3. Press Ctrl+Win again or wait 30s silence → dictation stops
4. After 10min idle → model auto-unloads; next hotkey press reloads it
