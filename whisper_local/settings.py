"""Settings persistence — loads/saves settings.json."""

import json
import os
import sys
import winreg

VALID_MODEL_SIZES = ("tiny", "base", "small", "turbo")
VALID_OUTPUT_MODES = ("type", "clipboard", "both")

DEFAULTS = {
    "model_size": "turbo",
    "output_mode": "type",
    "run_on_startup": False,
}


class Settings:
    """Manages application settings backed by a JSON file."""

    def __init__(self, path: str = "settings.json"):
        self._path = path
        self._data = dict(DEFAULTS)
        self._load()

    def _load(self) -> None:
        """Load settings from disk, or create defaults if missing."""
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    stored = json.load(f)
                # Merge stored values into defaults (only known keys)
                for key in DEFAULTS:
                    if key in stored:
                        self._data[key] = stored[key]
            except (json.JSONDecodeError, OSError):
                pass  # Use defaults on corrupt file
        # Always save to ensure file exists with all keys
        self.save()

    def save(self) -> None:
        """Write current settings to disk."""
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2)

    @property
    def model_size(self) -> str:
        return self._data["model_size"]

    @model_size.setter
    def model_size(self, value: str) -> None:
        if value in VALID_MODEL_SIZES:
            self._data["model_size"] = value

    @property
    def output_mode(self) -> str:
        return self._data["output_mode"]

    @output_mode.setter
    def output_mode(self, value: str) -> None:
        if value in VALID_OUTPUT_MODES:
            self._data["output_mode"] = value

    @property
    def run_on_startup(self) -> bool:
        return self._data["run_on_startup"]

    @run_on_startup.setter
    def run_on_startup(self, value: bool) -> None:
        self._data["run_on_startup"] = bool(value)


# Registry key for run-on-startup (HKCU, no admin needed)
_REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_REGISTRY_NAME = "WhisperLocal"


def set_startup_registry(enable: bool) -> None:
    """Add or remove Whisper Local from Windows startup registry.

    Uses HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run.
    No admin rights required.
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REGISTRY_KEY, 0, winreg.KEY_SET_VALUE
        )
        if enable:
            # Point to launch.vbs for silent startup (no console window)
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            launch_vbs = os.path.join(app_dir, "launch.vbs")
            # Use wscript to run VBS silently
            winreg.SetValueEx(
                key, _REGISTRY_NAME, 0, winreg.REG_SZ,
                f'wscript.exe "{launch_vbs}"'
            )
        else:
            try:
                winreg.DeleteValue(key, _REGISTRY_NAME)
            except FileNotFoundError:
                pass  # Already removed
        winreg.CloseKey(key)
    except OSError:
        pass  # Silently fail if registry access fails


def is_startup_enabled() -> bool:
    """Check if Whisper Local is in the startup registry."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REGISTRY_KEY, 0, winreg.KEY_READ
        )
        try:
            winreg.QueryValueEx(key, _REGISTRY_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except OSError:
        return False
