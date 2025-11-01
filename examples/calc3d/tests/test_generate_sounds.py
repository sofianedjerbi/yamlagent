"""Tests for sound generation functions."""

import struct
import wave
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from generate_sounds import (
    generate_beep,
    generate_chord,
    generate_tone_wave,
    save_wav,
)


class TestGenerateToneWave:
    """Tests for generate_tone_wave function."""

    def test_returns_list_of_samples(self):
        """Test that generate_tone_wave returns a list of integer samples."""
        samples = generate_tone_wave(440, 0.1)

        assert isinstance(samples, list)
        assert len(samples) > 0
        assert all(isinstance(s, int) for s in samples)

    def test_sample_count_matches_duration(self):
        """Test that number of samples matches duration and sample rate."""
        sample_rate = 44100
        duration = 0.1
        samples = generate_tone_wave(440, duration, sample_rate)

        expected_samples = int(sample_rate * duration)
        assert len(samples) == expected_samples

    def test_samples_within_valid_range(self):
        """Test that samples are within 16-bit signed integer range."""
        samples = generate_tone_wave(440, 0.1)

        assert all(-32768 <= s <= 32767 for s in samples)

    def test_different_frequencies_produce_different_patterns(self):
        """Test that different frequencies generate different waveforms."""
        samples_440 = generate_tone_wave(440, 0.01, sample_rate=44100)
        samples_880 = generate_tone_wave(880, 0.01, sample_rate=44100)

        # Different frequencies should produce different patterns
        assert samples_440 != samples_880

    def test_zero_duration_returns_empty_list(self):
        """Test that zero duration produces empty sample list."""
        samples = generate_tone_wave(440, 0)

        assert len(samples) == 0

    def test_volume_affects_amplitude(self):
        """Test that volume parameter affects sample amplitude."""
        samples_low = generate_tone_wave(440, 0.01, volume=0.1)
        samples_high = generate_tone_wave(440, 0.01, volume=0.9)

        # Higher volume should generally produce higher absolute values
        avg_low = sum(abs(s) for s in samples_low) / len(samples_low)
        avg_high = sum(abs(s) for s in samples_high) / len(samples_high)

        assert avg_high > avg_low


class TestSaveWav:
    """Tests for save_wav function."""

    def test_creates_valid_wav_file(self):
        """Test that save_wav creates a valid WAV file."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.wav"
            samples = generate_tone_wave(440, 0.05)

            save_wav(filepath, samples)

            assert filepath.exists()
            assert filepath.stat().st_size > 0

    def test_wav_file_has_correct_properties(self):
        """Test that generated WAV has correct audio properties."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.wav"
            sample_rate = 44100
            duration = 0.1
            samples = generate_tone_wave(440, duration, sample_rate)

            save_wav(filepath, samples, sample_rate)

            with wave.open(str(filepath), 'rb') as wav:
                assert wav.getnchannels() == 1  # Mono
                assert wav.getsampwidth() == 2  # 16-bit
                assert wav.getframerate() == sample_rate
                assert wav.getnframes() == len(samples)

    def test_empty_samples_creates_silent_file(self):
        """Test that empty sample list creates valid but silent file."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "silent.wav"

            save_wav(filepath, [])

            assert filepath.exists()
            with wave.open(str(filepath), 'rb') as wav:
                assert wav.getnframes() == 0


class TestGenerateBeep:
    """Tests for generate_beep function."""

    def test_creates_wav_file(self):
        """Test that generate_beep creates a WAV file."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "beep.wav"

            generate_beep(800, 0.05, filepath)

            assert filepath.exists()
            assert filepath.stat().st_size > 1000  # More than 1KB

    def test_beep_duration_matches_specification(self):
        """Test that generated beep has correct duration."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "beep.wav"
            duration = 0.1

            generate_beep(800, duration, filepath)

            with wave.open(str(filepath), 'rb') as wav:
                actual_duration = wav.getnframes() / wav.getframerate()
                assert abs(actual_duration - duration) < 0.001  # Within 1ms


class TestGenerateChord:
    """Tests for generate_chord function."""

    def test_creates_wav_file_from_chord(self):
        """Test that generate_chord creates a WAV file."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "chord.wav"

            generate_chord([400, 500, 600], 0.1, filepath)

            assert filepath.exists()
            assert filepath.stat().st_size > 1000

    def test_chord_duration_matches_specification(self):
        """Test that generated chord has correct duration."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "chord.wav"
            duration = 0.15

            generate_chord([400, 500], duration, filepath)

            with wave.open(str(filepath), 'rb') as wav:
                actual_duration = wav.getnframes() / wav.getframerate()
                assert abs(actual_duration - duration) < 0.001

    def test_single_frequency_chord_similar_to_beep(self):
        """Test that chord with single frequency is similar to beep."""
        with TemporaryDirectory() as tmpdir:
            beep_path = Path(tmpdir) / "beep.wav"
            chord_path = Path(tmpdir) / "chord.wav"

            generate_beep(440, 0.05, beep_path)
            generate_chord([440], 0.05, chord_path)

            # Both should have similar file sizes
            beep_size = beep_path.stat().st_size
            chord_size = chord_path.stat().st_size
            assert abs(beep_size - chord_size) < 1000  # Within 1KB

    def test_empty_frequency_list_creates_silent_file(self):
        """Test that chord with no frequencies creates a valid file."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "silent_chord.wav"

            generate_chord([], 0.1, filepath)

            assert filepath.exists()
