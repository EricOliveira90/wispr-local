"""Global hotkey registration — system-wide keyboard shortcuts."""

import threading

import keyboard


class HotkeyManager:
    """Manages global hotkey registration and callbacks."""

    def __init__(self):
        self._hotkeys: list[str] = []
        self._bindings: list[tuple[str, callable]] = []

    def register(self, hotkey: str, callback: callable) -> None:
        """Register a global hotkey.

        Callbacks are dispatched on a separate thread so that long-running
        operations (model loading, transcription) do not block the keyboard
        listener thread and prevent other hotkeys from firing.

        Args:
            hotkey: Key combination string (e.g., 'ctrl+win', 'alt+win').
            callback: Function to call when hotkey is pressed.
        """

        def _threaded_callback():
            t = threading.Thread(target=callback, daemon=True)
            t.start()

        keyboard.add_hotkey(hotkey, _threaded_callback, suppress=False)
        self._hotkeys.append(hotkey)
        # Store binding only if not already tracked (avoid duplicates on resume)
        if not any(h == hotkey and cb is callback for h, cb in self._bindings):
            self._bindings.append((hotkey, callback))

    def pause(self) -> None:
        """Temporarily unregister all hotkeys.

        Use before simulated keystrokes (e.g. pyautogui) to prevent the
        keyboard hook from intercepting them and corrupting internal state.
        Call ``resume()`` afterwards to re-register.
        """
        for hotkey in self._hotkeys:
            try:
                keyboard.remove_hotkey(hotkey)
            except (KeyError, ValueError):
                pass
        self._hotkeys.clear()

    def resume(self) -> None:
        """Re-register all previously registered hotkeys after a ``pause()``."""
        for hotkey, callback in self._bindings:
            self.register(hotkey, callback)

    def unregister_all(self) -> None:
        """Unregister all registered hotkeys."""
        for hotkey in self._hotkeys:
            try:
                keyboard.remove_hotkey(hotkey)
            except (KeyError, ValueError):
                pass
        self._hotkeys.clear()
        self._bindings.clear()
