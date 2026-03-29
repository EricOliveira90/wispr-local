# Whisper Local — Spec

Local, privacy-first speech-to-text for Windows. CPU-only, no cloud/API keys. Types transcribed speech into any focused app.

## Dictation

- Global hotkey toggles recording on/off
- **Ctrl+Win** → English, **Alt+Win** → Portuguese
- Pressing same hotkey stops; pressing other hotkey switches language
- **Ctrl+Shift+Q** → quit app
- Output modes (configurable, default=Type to field):
  - **Type to field** — simulates keyboard input
  - **Clipboard only**
  - **Both**

## System Tray

Microphone icon in tray. Color = state:
- Gray=Idle (no model), Yellow=Loading, Dark Blue=Ready, Bright Blue=Listening EN, Green=Listening PT
- Right-click menu: start/stop, load/unload model, settings, quit

## Resource Management

- Model (~1–2 GB RAM) loaded on demand (first dictation)
- Auto-stop: 30s silence → stop listening (model stays loaded)
- Auto-unload: 10min idle after stop → unload model, free RAM
- Manual load/unload via tray menu
- Toast notifications on model load/unload events

## Settings

Persisted in `settings.json`, accessible from tray menu.

- **Model size** (only changeable when unloaded): Tiny / Base / Small / **Turbo** (default) — tradeoff: speed↔accuracy
- **Output mode**: Type to field (default) / Clipboard / Both
- **Run on startup**: registry-based, no admin needed

## Requirements

- Windows 10/11, Python 3.9+, microphone, ~2 GB disk (first-run model download)
- Network only for initial model download; fully offline after
- No admin rights required

## Typical Flow

1. Launch via `launch.bat` or auto-start → tray icon appears
2. Focus text field → hotkey → speak → text appears
3. Same hotkey or 30s silence → stop
4. 10min idle → model auto-unloads; reloads on next hotkey
