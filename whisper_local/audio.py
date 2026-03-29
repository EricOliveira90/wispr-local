"""Audio capture — records from microphone via sounddevice."""

import numpy as np
import sounddevice as sd


def record_audio(
    duration: float,
    sample_rate: int = 16000,
    device: int | None = None,
) -> np.ndarray:
    """Record audio from the microphone.

    Args:
        duration: Recording duration in seconds.
        sample_rate: Sample rate in Hz (16000 is what Whisper expects).
        device: Audio input device index (None = default).

    Returns:
        Numpy array of audio samples (float32, mono, 1D).
    """
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        device=device,
    )
    sd.wait()
    return audio.flatten()


class AudioRecorder:
    """Manages continuous audio recording with start/stop control."""

    def __init__(self, sample_rate: int = 16000, device: int | None = None):
        self.sample_rate = sample_rate
        self.device = device
        self._stream = None
        self._chunks: list[np.ndarray] = []
        self._recording = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self) -> None:
        """Start recording audio from the microphone."""
        if self._recording:
            return
        self._chunks = []
        self._recording = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            device=self.device,
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        """Stop recording and return the captured audio.

        Returns:
            Numpy array of all recorded audio (float32, mono, 1D).
        """
        if not self._recording:
            return np.array([], dtype=np.float32)
        self._recording = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if not self._chunks:
            return np.array([], dtype=np.float32)
        return np.concatenate(self._chunks).flatten()

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for sounddevice InputStream — collects audio chunks."""
        if self._recording:
            self._chunks.append(indata.copy())
