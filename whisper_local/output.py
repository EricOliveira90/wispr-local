"""Text output delivery — type to field, clipboard, or both."""

import pyautogui
import pyperclip


def deliver_text(text: str, mode: str = "type") -> None:
    """Deliver transcribed text to the focused application.

    Args:
        text: The text to deliver.
        mode: Output mode — "type", "clipboard", or "both".
    """
    if not text:
        return

    if mode in ("type", "both"):
        type_text(text)

    if mode in ("clipboard", "both"):
        copy_to_clipboard(text)


def type_text(text: str) -> None:
    """Type text into the focused field via simulated keystrokes."""
    # Use pyautogui.write for ASCII, typewrite for special chars
    # interval=0.01 adds slight delay for reliability
    pyautogui.typewrite(text, interval=0.01) if text.isascii() else _type_unicode(text)


def _type_unicode(text: str) -> None:
    """Handle unicode/special characters by using clipboard paste."""
    old_clipboard = pyperclip.paste()
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    # Restore old clipboard after a brief delay
    import time
    time.sleep(0.1)
    pyperclip.copy(old_clipboard)


def copy_to_clipboard(text: str) -> None:
    """Copy text to the system clipboard."""
    pyperclip.copy(text)
