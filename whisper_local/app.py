"""Main app orchestrator — wires engine, tray, and all subsystems together."""

import threading

import pystray
from whisper_local.audio import AudioRecorder
from whisper_local.engine import TranscriptionEngine
from whisper_local.hotkeys import HotkeyManager
from whisper_local.output import deliver_text
from whisper_local.settings import Settings, set_startup_registry
from whisper_local.tray import create_tray_icon, update_tray_state


class WhisperLocalApp:
    """Orchestrates the Whisper Local application."""

    # Default timeouts (seconds)
    SILENCE_TIMEOUT = 3     # Auto-stop after 3s silence
    IDLE_TIMEOUT = 600      # Auto-unload after 10min idle

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.engine = TranscriptionEngine()
        self.recorder = AudioRecorder()
        self.hotkeys = HotkeyManager()
        self._icon = None
        self._current_language = None
        self._output_mode = self.settings.output_mode
        self._idle_timeout = self.IDLE_TIMEOUT
        self._idle_timer = None

    def _update_icon(self, state: str) -> None:
        """Update tray icon to reflect the given state."""
        if self._icon is not None:
            update_tray_state(self._icon, state)

    def _start_idle_timer(self) -> None:
        """Start the idle timer. When it fires, auto-unload the model."""
        self._cancel_idle_timer()
        self._idle_timer = threading.Timer(self._idle_timeout, self._on_idle_timeout)
        self._idle_timer.daemon = True
        self._idle_timer.start()

    def _cancel_idle_timer(self) -> None:
        """Cancel the idle timer if running."""
        if self._idle_timer is not None:
            self._idle_timer.cancel()
            self._idle_timer = None

    def _on_idle_timeout(self) -> None:
        """Called when idle timer fires — auto-unload model."""
        if self.engine.state == "ready":
            self.on_unload_model()

    def on_load_model(self) -> None:
        """Handle 'Load Model' menu action."""
        if self.engine.state != "idle":
            return
        self._update_icon("loading")
        self.engine.load_model(self.settings.model_size)
        self._update_icon("ready")

    def on_unload_model(self) -> None:
        """Handle 'Unload Model' menu action."""
        if self.engine.state != "ready":
            return
        self._cancel_idle_timer()
        self.engine.unload_model()
        self._update_icon("idle")

    def on_hotkey_en(self) -> str | None:
        """Handle Ctrl+Win hotkey — toggle English dictation."""
        return self._toggle_dictation("en")

    def on_hotkey_pt(self) -> str | None:
        """Handle Alt+Win hotkey — toggle Portuguese dictation."""
        return self._toggle_dictation("pt")

    def on_hotkey_quit(self) -> None:
        """Handle Ctrl+Shift+Q hotkey — quit the app."""
        self.on_quit()

    def _toggle_dictation(self, language: str) -> str | None:
        """Toggle dictation for the given language.

        If not recording: start dictation in the given language.
        If recording same language: stop and transcribe.
        If recording different language: stop current, start new language.

        Returns:
            Transcribed text if stopping, None if starting.
        """
        if self.recorder.is_recording:
            if self._current_language == language:
                # Same hotkey pressed again — stop and transcribe
                return self.on_stop_dictation()
            else:
                # Different language — stop current, start new
                self.on_stop_dictation()
                self.on_start_dictation(language)
                return None
        else:
            self.on_start_dictation(language)
            return None

    def on_start_dictation(self, language: str = "en") -> None:
        """Start recording audio for dictation.

        Args:
            language: Language code for transcription (en, pt, etc.).
        """
        if self.engine.state == "idle":
            self.on_load_model()

        if self.engine.state != "ready":
            return

        self._cancel_idle_timer()
        self._current_language = language
        icon_state = "listening_en" if language == "en" else "listening_pt"
        self._update_icon(icon_state)
        self.recorder.start()

    def on_stop_dictation(self) -> str:
        """Stop recording and transcribe the captured audio.

        Returns:
            Transcribed text string.
        """
        audio = self.recorder.stop()
        self._update_icon("ready")

        if len(audio) == 0:
            return ""

        text = self.engine.transcribe(audio, language=self._current_language)
        if text:
            print(f"📝 {text}")
            self.hotkeys.pause()
            try:
                deliver_text(text, mode=self._output_mode)
            finally:
                self.hotkeys.resume()
        self._current_language = None
        return text

    def set_output_mode(self, mode: str) -> None:
        """Set the output mode. Takes effect on next transcription.

        Args:
            mode: "type", "clipboard", or "both".
        """
        if mode in ("type", "clipboard", "both"):
            self._output_mode = mode

    def on_quit(self) -> None:
        """Handle 'Quit' menu action."""
        self.hotkeys.unregister_all()
        if self.recorder.is_recording:
            self.recorder.stop()
        if self.engine.state == "ready":
            self.engine.unload_model()
        if self._icon is not None:
            self._icon.stop()

    def _set_output_mode_and_save(self, mode: str) -> None:
        """Set output mode and persist to settings."""
        self.set_output_mode(mode)
        self.settings.output_mode = mode
        self.settings.save()

    def _set_model_size(self, size: str) -> None:
        """Set model size in settings (only when model is unloaded)."""
        if self.engine.state == "idle":
            self.settings.model_size = size
            self.settings.save()

    def _toggle_startup(self) -> None:
        """Toggle run-on-startup setting."""
        new_value = not self.settings.run_on_startup
        self.settings.run_on_startup = new_value
        self.settings.save()
        set_startup_registry(new_value)

    def _build_menu(self) -> list[pystray.MenuItem]:
        """Build the tray context menu items."""
        output_menu = pystray.Menu(
            pystray.MenuItem(
                "Type to field",
                lambda: self._set_output_mode_and_save("type"),
                checked=lambda item: self._output_mode == "type",
            ),
            pystray.MenuItem(
                "Clipboard only",
                lambda: self._set_output_mode_and_save("clipboard"),
                checked=lambda item: self._output_mode == "clipboard",
            ),
            pystray.MenuItem(
                "Both",
                lambda: self._set_output_mode_and_save("both"),
                checked=lambda item: self._output_mode == "both",
            ),
        )

        model_menu = pystray.Menu(
            pystray.MenuItem(
                "Tiny",
                lambda: self._set_model_size("tiny"),
                checked=lambda item: self.settings.model_size == "tiny",
                enabled=lambda item: self.engine.state == "idle",
            ),
            pystray.MenuItem(
                "Base",
                lambda: self._set_model_size("base"),
                checked=lambda item: self.settings.model_size == "base",
                enabled=lambda item: self.engine.state == "idle",
            ),
            pystray.MenuItem(
                "Small",
                lambda: self._set_model_size("small"),
                checked=lambda item: self.settings.model_size == "small",
                enabled=lambda item: self.engine.state == "idle",
            ),
            pystray.MenuItem(
                "Turbo",
                lambda: self._set_model_size("turbo"),
                checked=lambda item: self.settings.model_size == "turbo",
                enabled=lambda item: self.engine.state == "idle",
            ),
        )

        return [
            pystray.MenuItem("Load Model", lambda: self.on_load_model()),
            pystray.MenuItem("Unload Model", lambda: self.on_unload_model()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Output Mode", output_menu),
            pystray.MenuItem("Model Size", model_menu),
            pystray.MenuItem(
                "Run on Startup",
                lambda: self._toggle_startup(),
                checked=lambda item: self.settings.run_on_startup,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda: self.on_quit()),
        ]

    def _register_hotkeys(self) -> None:
        """Register global hotkeys for dictation and quit."""
        self.hotkeys.register("ctrl+windows", self.on_hotkey_en)
        self.hotkeys.register("alt+windows", self.on_hotkey_pt)
        self.hotkeys.register("ctrl+shift+q", self.on_hotkey_quit)

    def run(self) -> None:
        """Start the application — creates tray icon and enters main loop."""
        self._register_hotkeys()
        menu_items = self._build_menu()
        self._icon = create_tray_icon(menu_items, initial_state="idle")
        self._icon.run()


def main():
    """Entry point for the application."""
    app = WhisperLocalApp()
    app.run()


if __name__ == "__main__":
    main()
