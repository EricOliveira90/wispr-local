"""Tests for the transcription engine — model lifecycle and state management."""

from unittest.mock import MagicMock, patch

import numpy as np


def test_engine_starts_in_idle_state():
    """Engine starts with no model loaded, state is IDLE."""
    from whisper_local.engine import TranscriptionEngine

    engine = TranscriptionEngine()
    assert engine.state == "idle"
    assert engine.model is None


def test_engine_transcribes_audio_and_returns_text():
    """Engine transcribes audio array and returns full text string."""
    from whisper_local.engine import TranscriptionEngine

    engine = TranscriptionEngine()

    # Create mock segment objects
    mock_seg1 = MagicMock()
    mock_seg1.text = " Hello world"
    mock_seg1.start = 0.0
    mock_seg1.end = 1.5

    mock_seg2 = MagicMock()
    mock_seg2.text = " how are you"
    mock_seg2.start = 1.5
    mock_seg2.end = 3.0

    mock_info = MagicMock()
    mock_info.language = "en"
    mock_info.language_probability = 0.95

    mock_model = MagicMock()
    mock_model.transcribe.return_value = (iter([mock_seg1, mock_seg2]), mock_info)

    with patch("whisper_local.engine.WhisperModel", return_value=mock_model):
        engine.load_model()

    # Transcribe a fake audio array
    audio = np.zeros(16000, dtype=np.float32)  # 1 second of silence
    result = engine.transcribe(audio, language="en")

    assert result == "Hello world how are you"
    mock_model.transcribe.assert_called_once()


def test_load_model_ignored_when_already_ready():
    """Loading when already ready does nothing (no double-load)."""
    from whisper_local.engine import TranscriptionEngine

    engine = TranscriptionEngine()

    mock_model = MagicMock()
    with patch("whisper_local.engine.WhisperModel", return_value=mock_model) as mock_cls:
        engine.load_model("turbo")
        engine.load_model("turbo")  # second call should be ignored

    # WhisperModel constructor called only once
    assert mock_cls.call_count == 1
    assert engine.state == "ready"


def test_unload_model_ignored_when_idle():
    """Unloading when already idle does nothing."""
    from whisper_local.engine import TranscriptionEngine

    engine = TranscriptionEngine()
    engine.unload_model()  # should be a no-op

    assert engine.state == "idle"
    assert engine.model is None


def test_engine_load_uses_default_turbo_model():
    """Engine defaults to turbo model size with CPU int8."""
    from whisper_local.engine import TranscriptionEngine

    engine = TranscriptionEngine()

    with patch("whisper_local.engine.WhisperModel") as mock_cls:
        engine.load_model()

    mock_cls.assert_called_once_with("turbo", device="cpu", compute_type="int8")


def test_engine_loads_model_and_becomes_ready():
    """Loading a model transitions state from idle to ready, model is available."""
    from whisper_local.engine import TranscriptionEngine

    engine = TranscriptionEngine()

    # Mock faster-whisper at the system boundary
    mock_model = MagicMock()
    with patch("whisper_local.engine.WhisperModel", return_value=mock_model):
        engine.load_model("turbo")

    assert engine.state == "ready"
    assert engine.model is mock_model


def test_engine_unloads_model_and_returns_to_idle():
    """Unloading a model transitions state from ready back to idle, frees model."""
    from whisper_local.engine import TranscriptionEngine

    engine = TranscriptionEngine()

    mock_model = MagicMock()
    with patch("whisper_local.engine.WhisperModel", return_value=mock_model):
        engine.load_model("turbo")

    engine.unload_model()

    assert engine.state == "idle"
    assert engine.model is None
