"""Transcription engine — wraps faster-whisper with model lifecycle management."""

import numpy as np
from faster_whisper import WhisperModel


class TranscriptionEngine:
    """Manages the faster-whisper model lifecycle and transcription."""

    def __init__(self):
        self._model = None
        self._state = "idle"

    @property
    def state(self) -> str:
        """Current engine state: idle, loading, ready, listening."""
        return self._state

    @property
    def model(self):
        """The loaded WhisperModel instance, or None."""
        return self._model

    def load_model(self, model_size: str = "turbo") -> None:
        """Load a faster-whisper model. Transitions: idle → loading → ready."""
        if self._state not in ("idle",):
            return
        self._state = "loading"
        self._model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self._state = "ready"

    def unload_model(self) -> None:
        """Unload the model and free RAM. Transitions: ready → idle."""
        if self._state not in ("ready",):
            return
        self._model = None
        self._state = "idle"

    def transcribe(
        self,
        audio: np.ndarray,
        language: str | None = "en",
        beam_size: int = 5,
    ) -> str:
        """Transcribe audio and return the full text.

        Args:
            audio: Numpy array of audio samples (float32, 16kHz mono).
            language: Language code or None for auto-detect.
            beam_size: Beam size for decoding.

        Returns:
            Transcribed text as a single string.
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        segments, info = self._model.transcribe(
            audio,
            beam_size=beam_size,
            language=language,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=300,
            ),
        )

        text_parts = []
        for segment in segments:
            text_parts.append(segment.text.strip())

        return " ".join(text_parts)
