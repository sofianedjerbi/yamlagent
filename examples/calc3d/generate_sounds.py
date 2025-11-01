#!/usr/bin/env python3
"""
Generate sound effects for Calc3D calculator.

Creates simple tone-based sound effects using numpy and scipy.
Each sound has a distinct frequency and duration for different actions.
"""

import struct
import wave
from pathlib import Path


def generate_tone_wave(frequency: float, duration: float, sample_rate: int = 44100, volume: float = 0.3) -> bytes:
    """
    Generate a sine wave tone as raw audio data.

    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        volume: Volume level (0.0 to 1.0)

    Returns:
        Raw audio data as bytes
    """
    import math

    num_samples = int(sample_rate * duration)
    samples = []

    for i in range(num_samples):
        # Generate sine wave with envelope (fade in/out)
        t = i / sample_rate

        # Apply envelope to prevent clicking
        envelope = 1.0
        fade_duration = 0.01  # 10ms fade in/out
        if t < fade_duration:
            envelope = t / fade_duration
        elif t > duration - fade_duration:
            envelope = (duration - t) / fade_duration

        # Generate sample
        sample = math.sin(2 * math.pi * frequency * t) * volume * envelope

        # Convert to 16-bit integer
        sample_int = int(sample * 32767)
        samples.append(sample_int)

    return samples


def save_wav(filename: Path, samples: list, sample_rate: int = 44100):
    """
    Save audio samples to a WAV file.

    Args:
        filename: Output file path
        samples: List of audio samples (16-bit integers)
        sample_rate: Sample rate in Hz
    """
    with wave.open(str(filename), 'wb') as wav_file:
        # Set WAV parameters: mono, 16-bit
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 2 bytes = 16 bits
        wav_file.setframerate(sample_rate)

        # Write samples
        for sample in samples:
            wav_file.writeframes(struct.pack('<h', sample))


def generate_beep(frequency: float, duration: float, output_file: Path):
    """
    Generate a simple beep sound.

    Args:
        frequency: Beep frequency in Hz
        duration: Duration in seconds
        output_file: Output file path
    """
    print(f"Generating {output_file.name}: {frequency}Hz, {duration}s")
    samples = generate_tone_wave(frequency, duration)
    save_wav(output_file, samples)


def generate_chord(frequencies: list, duration: float, output_file: Path):
    """
    Generate a chord (multiple frequencies played together).

    Args:
        frequencies: List of frequencies in Hz
        duration: Duration in seconds
        output_file: Output file path
    """
    print(f"Generating {output_file.name}: chord {frequencies}, {duration}s")
    import math

    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate

        # Apply envelope
        envelope = 1.0
        fade_duration = 0.01
        if t < fade_duration:
            envelope = t / fade_duration
        elif t > duration - fade_duration:
            envelope = (duration - t) / fade_duration

        # Mix all frequencies
        sample = 0
        for freq in frequencies:
            sample += math.sin(2 * math.pi * freq * t) / len(frequencies)

        sample *= 0.3 * envelope
        sample_int = int(sample * 32767)
        samples.append(sample_int)

    save_wav(output_file, samples)


def main():
    """Generate all calculator sound effects."""
    # Get sounds directory
    sounds_dir = Path(__file__).parent / "src" / "calc3d" / "static" / "sounds"
    sounds_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating sound effects in {sounds_dir}")
    print("=" * 60)

    # Define sound specifications
    # Each sound has a distinct character for different calculator actions

    # Digit: Short, mid-frequency click (pleasant feedback)
    generate_beep(800, 0.05, sounds_dir / "digit.wav")

    # Operator: Lower tone, slightly longer (different from digit)
    generate_beep(600, 0.08, sounds_dir / "operator.wav")

    # Equals: Higher, rising tone (satisfying "completion" sound)
    # Create a rising tone effect
    samples = []
    sample_rate = 44100
    duration = 0.15
    num_samples = int(sample_rate * duration)

    import math
    for i in range(num_samples):
        t = i / sample_rate
        # Frequency rises from 600 to 1200 Hz
        freq = 600 + (600 * (t / duration))

        # Envelope
        envelope = 1.0
        fade_duration = 0.01
        if t < fade_duration:
            envelope = t / fade_duration
        elif t > duration - fade_duration:
            envelope = (duration - t) / fade_duration

        sample = math.sin(2 * math.pi * freq * t) * 0.3 * envelope
        sample_int = int(sample * 32767)
        samples.append(sample_int)

    print(f"Generating equals.wav: rising tone 600-1200Hz, {duration}s")
    save_wav(sounds_dir / "equals.wav", samples)

    # Clear: Falling tone (opposite of equals, "reset" feeling)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        # Frequency falls from 1000 to 400 Hz
        freq = 1000 - (600 * (t / duration))

        # Envelope
        envelope = 1.0
        if t < fade_duration:
            envelope = t / fade_duration
        elif t > duration - fade_duration:
            envelope = (duration - t) / fade_duration

        sample = math.sin(2 * math.pi * freq * t) * 0.3 * envelope
        sample_int = int(sample * 32767)
        samples.append(sample_int)

    print(f"Generating clear.wav: falling tone 1000-400Hz, {duration}s")
    save_wav(sounds_dir / "clear.wav", samples)

    # Error: Dissonant chord (unpleasant, attention-grabbing)
    generate_chord([400, 450, 320], 0.2, sounds_dir / "error.wav")

    print("=" * 60)
    print("✅ Sound generation complete!")
    print("\nGenerated files:")
    for sound_file in sorted(sounds_dir.glob("*.wav")):
        size = sound_file.stat().st_size
        print(f"  - {sound_file.name}: {size:,} bytes")


if __name__ == "__main__":
    main()
