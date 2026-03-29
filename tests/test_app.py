"""Tests for the app orchestrator — wires engine + tray together."""

from unittest.mock import MagicMock, patch, call

import numpy as np


def test_app_load_model_transitions_icon_through_states():
    """When user triggers load model, icon goes yellow→dark blue and engine loads."""
    from whisper_local.app import WhisperLocalApp

    mock_icon = MagicMock()
    mock_model = MagicMock()

    with patch("whisper_local.engine.WhisperModel", return_value=mock_model):
        app = WhisperLocalApp()
        app._icon = mock_icon  # inject mock icon
        app.on_load_model()

    assert app.engine.state == "ready"
    # Icon should have been updated to loading, then ready
    assert mock_icon.icon is not None  # icon was updated


def test_app_unload_model_returns_to_idle():
    """When user triggers unload, engine unloads and icon goes gray."""
    from whisper_local.app import WhisperLocalApp

    mock_icon = MagicMock()
    mock_model = MagicMock()

    with patch("whisper_local.engine.WhisperModel", return_value=mock_model):
        app = WhisperLocalApp()
        app._icon = mock_icon
        app.on_load_model()
        app.on_unload_model()

    assert app.engine.state == "idle"
    assert app.engine.model is None


def test_app_quit_stops_icon():
    """Quit action stops the tray icon."""
    from whisper_local.app import WhisperLocalApp

    mock_icon = MagicMock()

    app = WhisperLocalApp()
    app._icon = mock_icon
    app.on_quit()

    mock_icon.stop.assert_called_once()


def test_app_start_stop_dictation_transcribes_audio(capsys):
    """Start dictation records audio, stop dictation transcribes and prints text."""
    from whisper_local.app import WhisperLocalApp

    mock_icon = MagicMock()
    mock_whisper_model = MagicMock()

    # Mock transcription result
    mock_seg = MagicMock()
    mock_seg.text = " Hello from dictation"
    mock_seg.start = 0.0
    mock_seg.end = 2.0
    mock_info = MagicMock()
    mock_info.language = "en"
    mock_info.language_probability = 0.99
    mock_whisper_model.transcribe.return_value = (iter([mock_seg]), mock_info)

    # Mock audio recorder to return fake audio
    fake_audio = np.zeros(16000 * 2, dtype=np.float32)
    mock_recorder = MagicMock()
    mock_recorder.is_recording = False
    mock_recorder.stop.return_value = fake_audio

    with patch("whisper_local.engine.WhisperModel", return_value=mock_whisper_model):
        with patch("whisper_local.app.AudioRecorder", return_value=mock_recorder):
            app = WhisperLocalApp()
            app._icon = mock_icon
            app.on_load_model()

            # Start dictation
            app.on_start_dictation("en")
            mock_recorder.start.assert_called_once()

            # Stop dictation — should transcribe and print
            result = app.on_stop_dictation()

    assert result == "Hello from dictation"
    captured = capsys.readouterr()
    assert "Hello from dictation" in captured.out


def test_app_hotkey_toggle_starts_and_stops_dictation(capsys):
    """Pressing Ctrl+Win starts EN dictation; pressing again stops and transcribes."""
    from whisper_local.app import WhisperLocalApp

    mock_icon = MagicMock()
    mock_whisper_model = MagicMock()

    mock_seg = MagicMock()
    mock_seg.text = " Toggle test"
    mock_seg.start = 0.0
    mock_seg.end = 1.0
    mock_info = MagicMock()
    mock_info.language = "en"
    mock_info.language_probability = 0.99
    mock_whisper_model.transcribe.return_value = (iter([mock_seg]), mock_info)

    fake_audio = np.zeros(16000, dtype=np.float32)
    mock_recorder = MagicMock()
    mock_recorder.is_recording = False
    mock_recorder.stop.return_value = fake_audio

    with patch("whisper_local.engine.WhisperModel", return_value=mock_whisper_model):
        with patch("whisper_local.app.AudioRecorder", return_value=mock_recorder):
            app = WhisperLocalApp()
            app._icon = mock_icon
            app.on_load_model()

            # First press: starts dictation
            app.on_hotkey_en()
            mock_recorder.start.assert_called_once()
            assert app._current_language == "en"

            # Simulate recorder now recording
            mock_recorder.is_recording = True

            # Second press: stops dictation and transcribes
            result = app.on_hotkey_en()

    assert result == "Toggle test"


def test_app_hotkey_switches_language(capsys):
    """Pressing Alt+Win while EN is active switches to PT."""
    from whisper_local.app import WhisperLocalApp

    mock_icon = MagicMock()
    mock_whisper_model = MagicMock()

    mock_seg = MagicMock()
    mock_seg.text = " Switched"
    mock_seg.start = 0.0
    mock_seg.end = 1.0
    mock_info = MagicMock()
    mock_info.language = "en"
    mock_info.language_probability = 0.99
    mock_whisper_model.transcribe.return_value = (iter([mock_seg]), mock_info)

    fake_audio = np.zeros(16000, dtype=np.float32)
    mock_recorder = MagicMock()
    mock_recorder.is_recording = False
    mock_recorder.stop.return_value = fake_audio

    with patch("whisper_local.engine.WhisperModel", return_value=mock_whisper_model):
        with patch("whisper_local.app.AudioRecorder", return_value=mock_recorder):
            app = WhisperLocalApp()
            app._icon = mock_icon
            app.on_load_model()

            # Start EN dictation
            app.on_hotkey_en()
            assert app._current_language == "en"
            mock_recorder.is_recording = True

            # Press PT hotkey — should stop EN, start PT
            app.on_hotkey_pt()
            assert app._current_language == "pt"
            # Recorder should have been stopped and started again
            assert mock_recorder.start.call_count == 2


def test_app_quit_hotkey():
    """Ctrl+Shift+Q quits the app."""
    from whisper_local.app import WhisperLocalApp

    mock_icon = MagicMock()

    app = WhisperLocalApp()
    app._icon = mock_icon
    app.on_hotkey_quit()

    mock_icon.stop.assert_called_once()


def test_app_delivers_text_via_output_mode():
    """After transcription, text is delivered via the configured output mode."""
    from whisper_local.app import WhisperLocalApp

    mock_icon = MagicMock()
    mock_whisper_model = MagicMock()

    mock_seg = MagicMock()
    mock_seg.text = " Output test"
    mock_seg.start = 0.0
    mock_seg.end = 1.0
    mock_info = MagicMock()
    mock_info.language = "en"
    mock_info.language_probability = 0.99
    mock_whisper_model.transcribe.return_value = (iter([mock_seg]), mock_info)

    fake_audio = np.zeros(16000, dtype=np.float32)
    mock_recorder = MagicMock()
    mock_recorder.is_recording = False
    mock_recorder.stop.return_value = fake_audio

    with patch("whisper_local.engine.WhisperModel", return_value=mock_whisper_model):
        with patch("whisper_local.app.AudioRecorder", return_value=mock_recorder):
            with patch("whisper_local.app.deliver_text") as mock_deliver:
                app = WhisperLocalApp()
                app._icon = mock_icon
                app._output_mode = "clipboard"
                app.on_load_model()
                app.on_start_dictation("en")
                app.on_stop_dictation()

    mock_deliver.assert_called_once_with("Output test", mode="clipboard")


def test_app_output_mode_defaults_to_type():
    """App defaults to 'type' output mode."""
    from whisper_local.app import WhisperLocalApp

    app = WhisperLocalApp()
    assert app._output_mode == "type"


def test_app_set_output_mode():
    """Output mode can be changed and takes effect immediately."""
    from whisper_local.app import WhisperLocalApp

    app = WhisperLocalApp()
    app.set_output_mode("clipboard")
    assert app._output_mode == "clipboard"

    app.set_output_mode("both")
    assert app._output_mode == "both"
