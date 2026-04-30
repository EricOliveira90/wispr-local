"""Tests for auto-stop on silence and auto-unload on idle."""

from unittest.mock import MagicMock, patch, PropertyMock
import time


def test_app_auto_unload_after_idle_timeout():
    """After stop, if idle for the configured timeout, model auto-unloads."""
    from whisper_local.app import WhisperLocalApp

    mock_icon = MagicMock()
    mock_model = MagicMock()

    with patch("whisper_local.engine.WhisperModel", return_value=mock_model):
        app = WhisperLocalApp()
        app._icon = mock_icon
        app._idle_timeout = 0.1  # 100ms for testing (normally 600s)
        app.on_load_model()

        assert app.engine.state == "ready"

        # Simulate stop dictation triggering idle timer
        app._start_idle_timer()

        # Wait for timer to fire
        time.sleep(0.3)

    assert app.engine.state == "idle"
    assert app.engine.model is None


def test_app_idle_timer_cancelled_on_new_dictation():
    """Starting new dictation cancels the idle timer."""
    from whisper_local.app import WhisperLocalApp
    import numpy as np

    mock_icon = MagicMock()
    mock_model = MagicMock()
    mock_recorder = MagicMock()
    mock_recorder.is_recording = False

    with patch("whisper_local.engine.WhisperModel", return_value=mock_model):
        with patch("whisper_local.app.AudioRecorder", return_value=mock_recorder):
            app = WhisperLocalApp()
            app._icon = mock_icon
            app._idle_timeout = 0.2  # 200ms for testing
            app.on_load_model()

            # Start idle timer
            app._start_idle_timer()

            # Before timeout, start new dictation — should cancel timer
            time.sleep(0.05)
            app.on_start_dictation("en")

            # Wait past the original timeout
            time.sleep(0.3)

    # Model should still be loaded because dictation was started
    assert app.engine.state == "ready"


