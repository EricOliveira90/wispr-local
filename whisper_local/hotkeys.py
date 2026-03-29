"""Global hotkey registration — system-wide keyboard shortcuts."""

import keyboard


class HotkeyManager:
    """Manages global hotkey registration and callbacks."""

    def __init__(self):
        self._hotkeys: list[str] = []

    def register(self, hotkey: str, callback: callable) -> None:
        """Register a global hotkey.

        Args:
            hotkey: Key combination string (e.g., 'ctrl+win', 'alt+win').
            callback: Function to call when hotkey is pressed.
        """
        keyboard.add_hotkey(hotkey, callback, suppress=True)
        self._hotkeys.append(hotkey)

    def unregister_all(self) -> None:
        """Unregister all registered hotkeys."""
        for hotkey in self._hotkeys:
            try:
                keyboard.remove_hotkey(hotkey)
            except (KeyError, ValueError):
                pass
        self._hotkeys.clear()
