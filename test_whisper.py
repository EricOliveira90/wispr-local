"""
Faster-Whisper Simple Test Script
==================================
A minimal script to test faster-whisper transcription with live microphone input.

Usage:
    python test_whisper.py                    # Record from mic (default: English, base model)
    python test_whisper.py --lang pt          # Record from mic in Portuguese
    python test_whisper.py --model tiny       # Use tiny model (fastest, least accurate)
    python test_whisper.py --model turbo      # Use turbo model (best speed/accuracy)
    python test_whisper.py --file audio.wav   # Transcribe an audio file
    python test_whisper.py --duration 10      # Record for 10 seconds (default: 5)
    python test_whisper.py --list-devices     # List available audio input devices
    python test_whisper.py --device 1         # Use specific input device by index
"""

import argparse
import sys
import time
import wave
import tempfile
import os

import numpy as np


def list_audio_devices():
    """List all available audio input devices."""
    import sounddevice as sd

    print("\n🎤 Available Audio Input Devices:")
    print("-" * 60)
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:
            marker = " ← DEFAULT" if i == sd.default.device[0] else ""
            print(f"  [{i}] {dev['name']} (channels: {dev['max_input_channels']}){marker}")
    print()


def record_audio(duration: float, sample_rate: int = 16000, device: int | None = None) -> np.ndarray:
    """Record audio from the microphone.

    Args:
        duration: Recording duration in seconds.
        sample_rate: Sample rate in Hz (16000 is what Whisper expects).
        device: Audio input device index (None = default).

    Returns:
        Numpy array of audio samples (float32, mono).
    """
    import sounddevice as sd

    print(f"\n🎙️  Recording for {duration} seconds... Speak now!")
    print("=" * 40)

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        device=device,
    )
    
    # Show a simple progress bar
    for i in range(int(duration)):
        time.sleep(1)
        elapsed = i + 1
        bar = "█" * elapsed + "░" * (int(duration) - elapsed)
        print(f"\r  [{bar}] {elapsed}/{int(duration)}s", end="", flush=True)
    
    sd.wait()
    print("\n✅ Recording complete!\n")

    return audio.flatten()


def save_wav(audio: np.ndarray, path: str, sample_rate: int = 16000):
    """Save audio array to a WAV file for debugging/replay."""
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())


def transcribe_audio(
    audio_source: str | np.ndarray,
    model_size: str = "base",
    language: str | None = "en",
    beam_size: int = 5,
):
    """Transcribe audio using faster-whisper.

    Args:
        audio_source: Path to audio file or numpy array of audio samples.
        model_size: Whisper model size (tiny, base, small, medium, large-v3, turbo).
        language: Language code (en, pt, etc.) or None for auto-detect.
        beam_size: Beam size for decoding (higher = more accurate but slower).
    """
    from faster_whisper import WhisperModel

    print(f"📦 Loading model '{model_size}' (CPU, int8)...")
    print("   (First run will download the model — this may take a minute)\n")

    t0 = time.time()
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    load_time = time.time() - t0
    print(f"✅ Model loaded in {load_time:.1f}s\n")

    # Transcribe
    print("🔄 Transcribing...")
    t0 = time.time()

    segments, info = model.transcribe(
        audio_source,
        beam_size=beam_size,
        language=language,
        vad_filter=True,  # Filter out silence
        vad_parameters=dict(
            min_silence_duration_ms=500,
            speech_pad_ms=300,
        ),
    )

    # Collect results
    results = []
    for segment in segments:
        results.append(segment)
        print(f"  [{segment.start:.1f}s → {segment.end:.1f}s] {segment.text.strip()}")

    transcribe_time = time.time() - t0

    # Summary
    print("\n" + "=" * 60)
    print("📊 Results Summary")
    print("=" * 60)

    if info.language:
        print(f"  Language:       {info.language} (probability: {info.language_probability:.1%})")
    if info.duration:
        print(f"  Audio duration: {info.duration:.1f}s")
    print(f"  Segments:       {len(results)}")
    print(f"  Transcribe time: {transcribe_time:.2f}s")
    if info.duration and info.duration > 0:
        rtf = transcribe_time / info.duration
        print(f"  Real-time factor: {rtf:.2f}x {'(faster than real-time! ⚡)' if rtf < 1 else ''}")

    full_text = " ".join(seg.text.strip() for seg in results)
    print(f"\n📝 Full transcription:\n   \"{full_text}\"\n")

    return full_text


def transcribe_file(file_path: str, model_size: str = "base", language: str | None = "en", beam_size: int = 5):
    """Transcribe an audio file."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    print(f"📂 Transcribing file: {file_path}")
    return transcribe_audio(file_path, model_size=model_size, language=language, beam_size=beam_size)


def transcribe_microphone(
    duration: float = 5.0,
    model_size: str = "base",
    language: str | None = "en",
    beam_size: int = 5,
    device: int | None = None,
    save_recording: bool = False,
):
    """Record from microphone and transcribe."""
    audio = record_audio(duration, device=device)

    # Optionally save the recording
    if save_recording:
        wav_path = os.path.join(tempfile.gettempdir(), "whisper_test_recording.wav")
        save_wav(audio, wav_path)
        print(f"💾 Recording saved to: {wav_path}")

    return transcribe_audio(audio, model_size=model_size, language=language, beam_size=beam_size)


def main():
    parser = argparse.ArgumentParser(
        description="Faster-Whisper Simple Test — Record & Transcribe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_whisper.py                        # English, base model, 5s recording
  python test_whisper.py --lang pt --duration 8 # Portuguese, 8s recording
  python test_whisper.py --model turbo          # Use turbo model
  python test_whisper.py --file meeting.wav     # Transcribe a file
  python test_whisper.py --lang auto            # Auto-detect language
  python test_whisper.py --list-devices         # Show audio devices
  python test_whisper.py --save                 # Save recording as WAV
        """,
    )

    parser.add_argument(
        "--model", "-m",
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v3", "turbo"],
        help="Whisper model size (default: base). Larger = more accurate but slower.",
    )
    parser.add_argument(
        "--lang", "-l",
        default="en",
        help="Language code: en, pt, es, fr, etc. Use 'auto' for auto-detection. (default: en)",
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=5.0,
        help="Recording duration in seconds (default: 5).",
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="Path to an audio file to transcribe (skips microphone recording).",
    )
    parser.add_argument(
        "--beam-size", "-b",
        type=int,
        default=5,
        help="Beam size for decoding (default: 5).",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Audio input device index (use --list-devices to see options).",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio input devices and exit.",
    )
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Save the microphone recording as a WAV file.",
    )

    args = parser.parse_args()

    # Handle language
    language = None if args.lang == "auto" else args.lang

    print("╔══════════════════════════════════════════╗")
    print("║   🎤 Faster-Whisper Test Script          ║")
    print("╚══════════════════════════════════════════╝")

    if args.list_devices:
        list_audio_devices()
        return

    print(f"\n⚙️  Settings:")
    print(f"   Model:    {args.model}")
    print(f"   Language: {args.lang}")
    if args.file:
        print(f"   File:     {args.file}")
    else:
        print(f"   Duration: {args.duration}s")
        if args.device is not None:
            print(f"   Device:   {args.device}")

    if args.file:
        transcribe_file(args.file, model_size=args.model, language=language, beam_size=args.beam_size)
    else:
        transcribe_microphone(
            duration=args.duration,
            model_size=args.model,
            language=language,
            beam_size=args.beam_size,
            device=args.device,
            save_recording=args.save,
        )


if __name__ == "__main__":
    main()
