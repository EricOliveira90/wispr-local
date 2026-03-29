"""Tests for text output delivery modes."""

from unittest.mock import patch, call


def test_deliver_text_type_mode_calls_type():
    """Type mode simulates keyboard input."""
    from whisper_local.output import deliver_text

    with patch("whisper_local.output.type_text") as mock_type:
        with patch("whisper_local.output.copy_to_clipboard") as mock_clip:
            deliver_text("hello", mode="type")

    mock_type.assert_called_once_with("hello")
    mock_clip.assert_not_called()


def test_deliver_text_clipboard_mode_copies():
    """Clipboard mode copies text without typing."""
    from whisper_local.output import deliver_text

    with patch("whisper_local.output.type_text") as mock_type:
        with patch("whisper_local.output.copy_to_clipboard") as mock_clip:
            deliver_text("hello", mode="clipboard")

    mock_type.assert_not_called()
    mock_clip.assert_called_once_with("hello")


def test_deliver_text_both_mode_types_and_copies():
    """Both mode types AND copies to clipboard."""
    from whisper_local.output import deliver_text

    with patch("whisper_local.output.type_text") as mock_type:
        with patch("whisper_local.output.copy_to_clipboard") as mock_clip:
            deliver_text("hello", mode="both")

    mock_type.assert_called_once_with("hello")
    mock_clip.assert_called_once_with("hello")


def test_deliver_text_empty_string_does_nothing():
    """Empty text produces no output."""
    from whisper_local.output import deliver_text

    with patch("whisper_local.output.type_text") as mock_type:
        with patch("whisper_local.output.copy_to_clipboard") as mock_clip:
            deliver_text("", mode="type")

    mock_type.assert_not_called()
    mock_clip.assert_not_called()
