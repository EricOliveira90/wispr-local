# Plan: Whisper Local

> Source PRD: `SPEC.md` — Local, privacy-first speech-to-text for Windows

## Architectural decisions

Durable decisions that apply across all phases:

- **Runtime**: Python 3.9+, CPU-only, no cloud/API keys
- **Transcription engine**: `faster-whisper` with `int8` compute type, VAD filter enabled
- **Audio capture**: `sounddevice` at 16 kHz mono
- **System tray**: `pystray` with `Pillow` for icon rendering
- **Global hotkeys**: `keyboard` library (or `pynput`) for system-wide hotkey registration
- **Text output**: `pyautogui` / `pyperclip` for simulated keystrokes and clipboard
- **Settings file**: `settings.json` in the app directory, loaded at startup
- **Model cache**: Default HuggingFace cache (`%USERPROFILE%\.cache\huggingface`)
- **Tray icon states**:
  - Gray = Idle (no model loaded)
  - Yellow = Loading model
  - Dark Blue = Ready (model loaded, not listening)
  - Bright Blue = Listening (English)
  - Green = Listening (Portuguese)
- **Hotkey bindings**:
  - `Ctrl+Win` → Start/stop English dictation
  - `Alt+Win` → Start/stop Portuguese dictation
  - `Ctrl+Shift+Q` → Quit application
- **Model sizes**: Tiny, Base, Small, Turbo (default: Turbo)
- **Output modes**: Type to field (default), Clipboard only, Both
- **Timers**: 30s silence → auto-stop listening; 10min idle after stop → auto-unload model
- **Startup**: Registry-based run-on-startup (HKCU, no admin), `launch.bat` entry point

---

## Phase 1: Core Transcription Engine + Minimal Tray Icon

**User stories**: Basic app launch, model loading on demand, transcription pipeline, tray icon with state colors (Gray → Yellow → Dark Blue)

### What to build

A system tray application that shows a microphone icon reflecting the current model state. On first launch the icon is Gray (idle). The user can trigger model loading from the tray right-click menu; the icon turns Yellow while loading, then Dark Blue when ready. Once the model is loaded, a "Start Dictation" tray menu option records from the microphone, transcribes the audio, and prints the result to the console (output delivery comes in Phase 2). The transcription engine wraps `faster-whisper` with VAD filtering. This phase establishes the application's main loop, tray integration, and the core transcription pipeline end-to-end.

### Acceptance criteria

- [ ] Running the app shows a system tray icon (Gray)
- [ ] Right-click menu includes: Load Model, Start Dictation, Quit
- [ ] "Load Model" triggers model download/load; icon turns Yellow during load, Dark Blue when ready
- [ ] "Start Dictation" records from the default microphone and transcribes using faster-whisper
- [ ] Transcribed text is printed to console (placeholder for output delivery)
- [ ] "Quit" exits the application cleanly
- [ ] Model loads with Turbo size by default, CPU int8, VAD enabled

---

## Phase 2: Global Hotkey Dictation with Language Switching + Text Output Modes

**User stories**: Ctrl+Win → English, Alt+Win → Portuguese, same hotkey stops, other hotkey switches language, Ctrl+Shift+Q quits, tray icon Bright Blue (EN) / Green (PT), output modes (Type to field / Clipboard / Both)

### What to build

Replace the tray-menu-driven dictation with global hotkeys. Pressing Ctrl+Win starts English dictation (icon → Bright Blue); pressing it again stops. Pressing Alt+Win starts Portuguese dictation (icon → Green); pressing it again stops. If one language is active and the other hotkey is pressed, the current session stops and a new one starts in the other language. Ctrl+Shift+Q quits the app from anywhere. The model is loaded on demand when the first hotkey is pressed (lazy load, same as Phase 1 but triggered by hotkey instead of menu).

After transcription, text is delivered to the focused application via the configured output mode: simulated keystrokes ("Type to field"), clipboard write ("Clipboard only"), or both. The default mode is "Type to field" and can be changed via tray menu for now (settings persistence comes in Phase 4).

### Acceptance criteria

- [ ] Ctrl+Win toggles English dictation on/off from any application
- [ ] Alt+Win toggles Portuguese dictation on/off from any application
- [ ] Pressing the other language hotkey while listening switches language seamlessly
- [ ] Ctrl+Shift+Q quits the application from anywhere
- [ ] Tray icon shows Bright Blue while listening in English, Green while listening in Portuguese
- [ ] Model loads on demand when first hotkey is pressed (Yellow → Dark Blue → listening color)
- [ ] Transcribed text is typed into the focused field via simulated keystrokes (default mode)
- [ ] Clipboard-only and Both output modes work when selected from tray menu
- [ ] Tray right-click menu shows current output mode and allows switching

---

## Phase 3: Resource Management (Auto-stop, Auto-unload, Manual Controls)

**User stories**: 30s silence auto-stop, 10min idle auto-unload, manual load/unload via tray

### What to build

Add intelligent resource management to the dictation lifecycle. During active listening, if 30 seconds of silence are detected (no speech segments from VAD), dictation automatically stops and the icon returns to Dark Blue (ready). After dictation stops, a 10-minute idle timer begins; if no new dictation is started within that window, the model is unloaded from memory and the icon returns to Gray (idle). The tray menu gains explicit "Load Model" and "Unload Model" options for manual control. The tray icon color changes provide visual feedback for all state transitions.

### Acceptance criteria

- [ ] 30 seconds of continuous silence during listening triggers auto-stop
- [ ] After auto-stop or manual stop, icon returns to Dark Blue (model stays loaded)
- [ ] 10 minutes of idle after stop triggers automatic model unload; icon returns to Gray
- [ ] Tray menu includes "Load Model" and "Unload Model" options with correct enabled/disabled states
- [ ] Manual unload frees model from RAM; icon returns to Gray
- [ ] Next hotkey press after unload triggers fresh model load (Yellow → Dark Blue → listening)

---

## Phase 4: Settings, Persistence, Launch Script + Startup Polish

**User stories**: `settings.json` persistence, model size selection (only when unloaded), output mode setting, run-on-startup (registry-based, no admin), `launch.bat` entry point, end-to-end typical flow

### What to build

Add a settings system backed by `settings.json`. Settings are accessible from a "Settings" option in the tray menu (either a simple dialog or sub-menu). Available settings: model size (Tiny/Base/Small/Turbo — only changeable when model is unloaded), output mode (Type to field/Clipboard/Both), and run-on-startup toggle. The run-on-startup option writes or removes a registry entry under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (no admin required). Create `launch.bat` as the primary entry point that activates the Python environment and starts the app. Verify the complete typical flow: launch → tray icon → hotkey → speak → text appears → silence auto-stop → idle auto-unload → hotkey reloads.

### Acceptance criteria

- [ ] `settings.json` is created with defaults on first run if it doesn't exist
- [ ] Settings persist across app restarts
- [ ] Model size is selectable from settings (Tiny/Base/Small/Turbo); option is disabled when model is loaded
- [ ] Output mode is selectable from settings and takes effect immediately
- [ ] Run-on-startup toggle writes/removes HKCU registry entry correctly
- [ ] `launch.bat` starts the application correctly
- [ ] Full typical flow works end-to-end: launch → tray → hotkey → speak → text output → auto-stop → auto-unload → hotkey reload
