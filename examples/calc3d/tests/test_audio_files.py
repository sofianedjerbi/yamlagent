"""Tests for audio file validation and properties."""

import wave
from pathlib import Path

import pytest


class TestAudioFileProperties:
    """Tests for validating generated audio files."""

    @pytest.fixture
    def sounds_dir(self):
        """Path to sounds directory."""
        return Path(__file__).parent.parent / "src" / "calc3d" / "static" / "sounds"

    @pytest.fixture
    def sound_specs(self):
        """Expected specifications for each sound file."""
        return {
            'digit.wav': {
                'min_duration': 0.04,
                'max_duration': 0.06,
                'min_size': 1000
            },
            'operator.wav': {
                'min_duration': 0.07,
                'max_duration': 0.09,
                'min_size': 1000
            },
            'equals.wav': {
                'min_duration': 0.14,
                'max_duration': 0.16,
                'min_size': 1000
            },
            'clear.wav': {
                'min_duration': 0.14,
                'max_duration': 0.16,
                'min_size': 1000
            },
            'error.wav': {
                'min_duration': 0.19,
                'max_duration': 0.21,
                'min_size': 1000
            },
        }

    @pytest.mark.parametrize('filename', [
        'digit.wav',
        'operator.wav',
        'equals.wav',
        'clear.wav',
        'error.wav',
    ])
    def test_sound_file_exists(self, sounds_dir, filename):
        """Test that all sound files exist."""
        filepath = sounds_dir / filename
        assert filepath.exists(), f"{filename} not found"

    @pytest.mark.parametrize('filename', [
        'digit.wav',
        'operator.wav',
        'equals.wav',
        'clear.wav',
        'error.wav',
    ])
    def test_sound_file_is_valid_wav(self, sounds_dir, filename):
        """Test that sound file is a valid WAV format."""
        filepath = sounds_dir / filename

        # Should not raise exception when opening as WAV
        with wave.open(str(filepath), 'rb') as wav:
            assert wav.getnchannels() > 0

    @pytest.mark.parametrize('filename', [
        'digit.wav',
        'operator.wav',
        'equals.wav',
        'clear.wav',
        'error.wav',
    ])
    def test_sound_file_is_mono(self, sounds_dir, filename):
        """Test that sound file is mono (1 channel)."""
        filepath = sounds_dir / filename

        with wave.open(str(filepath), 'rb') as wav:
            assert wav.getnchannels() == 1

    @pytest.mark.parametrize('filename', [
        'digit.wav',
        'operator.wav',
        'equals.wav',
        'clear.wav',
        'error.wav',
    ])
    def test_sound_file_is_16bit(self, sounds_dir, filename):
        """Test that sound file is 16-bit audio."""
        filepath = sounds_dir / filename

        with wave.open(str(filepath), 'rb') as wav:
            assert wav.getsampwidth() == 2  # 2 bytes = 16 bits

    @pytest.mark.parametrize('filename', [
        'digit.wav',
        'operator.wav',
        'equals.wav',
        'clear.wav',
        'error.wav',
    ])
    def test_sound_file_is_44100hz(self, sounds_dir, filename):
        """Test that sound file has 44.1kHz sample rate."""
        filepath = sounds_dir / filename

        with wave.open(str(filepath), 'rb') as wav:
            assert wav.getframerate() == 44100

    def test_sound_file_durations(self, sounds_dir, sound_specs):
        """Test that all sound files have correct durations."""
        for filename, specs in sound_specs.items():
            filepath = sounds_dir / filename

            with wave.open(str(filepath), 'rb') as wav:
                duration = wav.getnframes() / wav.getframerate()

                assert specs['min_duration'] <= duration <= specs['max_duration'], \
                    f"{filename}: duration {duration:.3f}s not in range " \
                    f"{specs['min_duration']}-{specs['max_duration']}"

    def test_sound_file_sizes(self, sounds_dir, sound_specs):
        """Test that all sound files have reasonable sizes (not placeholders)."""
        for filename, specs in sound_specs.items():
            filepath = sounds_dir / filename
            size = filepath.stat().st_size

            assert size > specs['min_size'], \
                f"{filename}: size {size} bytes is too small (< {specs['min_size']})"

    def test_different_sounds_have_different_content(self, sounds_dir):
        """Test that sound files are unique (not duplicates)."""
        sound_files = ['digit.wav', 'operator.wav', 'equals.wav', 'clear.wav', 'error.wav']
        file_contents = {}

        for filename in sound_files:
            filepath = sounds_dir / filename
            with open(filepath, 'rb') as f:
                file_contents[filename] = f.read()

        # Compare each pair of files
        for i, file1 in enumerate(sound_files):
            for file2 in sound_files[i + 1:]:
                assert file_contents[file1] != file_contents[file2], \
                    f"{file1} and {file2} have identical content"


class TestSoundFileIntegrity:
    """Tests for sound file data integrity."""

    @pytest.fixture
    def sounds_dir(self):
        """Path to sounds directory."""
        return Path(__file__).parent.parent / "src" / "calc3d" / "static" / "sounds"

    def test_digit_sound_is_short_beep(self, sounds_dir):
        """Test that digit sound is a short beep (~50ms)."""
        filepath = sounds_dir / "digit.wav"

        with wave.open(str(filepath), 'rb') as wav:
            duration = wav.getnframes() / wav.getframerate()
            # Should be around 0.05 seconds
            assert 0.04 <= duration <= 0.06

    def test_operator_sound_is_medium_beep(self, sounds_dir):
        """Test that operator sound is slightly longer (~80ms)."""
        filepath = sounds_dir / "operator.wav"

        with wave.open(str(filepath), 'rb') as wav:
            duration = wav.getnframes() / wav.getframerate()
            # Should be around 0.08 seconds
            assert 0.07 <= duration <= 0.09

    def test_equals_and_clear_have_similar_duration(self, sounds_dir):
        """Test that equals and clear sounds have similar durations."""
        with wave.open(str(sounds_dir / "equals.wav"), 'rb') as wav:
            equals_duration = wav.getnframes() / wav.getframerate()

        with wave.open(str(sounds_dir / "clear.wav"), 'rb') as wav:
            clear_duration = wav.getnframes() / wav.getframerate()

        # Both should be around 0.15 seconds
        assert abs(equals_duration - clear_duration) < 0.01

    def test_error_sound_is_longest(self, sounds_dir):
        """Test that error sound is the longest duration."""
        durations = {}
        sound_files = ['digit.wav', 'operator.wav', 'equals.wav', 'clear.wav', 'error.wav']

        for filename in sound_files:
            with wave.open(str(sounds_dir / filename), 'rb') as wav:
                durations[filename] = wav.getnframes() / wav.getframerate()

        # Error should be the longest
        assert durations['error.wav'] == max(durations.values())

    def test_all_sounds_have_frames(self, sounds_dir):
        """Test that all sound files contain audio data."""
        sound_files = ['digit.wav', 'operator.wav', 'equals.wav', 'clear.wav', 'error.wav']

        for filename in sound_files:
            with wave.open(str(sounds_dir / filename), 'rb') as wav:
                frames = wav.getnframes()
                assert frames > 0, f"{filename} has no audio frames"

    def test_sounds_directory_exists(self, sounds_dir):
        """Test that sounds directory exists."""
        assert sounds_dir.exists(), "Sounds directory not found"
        assert sounds_dir.is_dir(), "Sounds path is not a directory"

    def test_no_extra_sound_files(self, sounds_dir):
        """Test that only expected sound files exist (no leftovers)."""
        expected_files = {
            'digit.wav',
            'operator.wav',
            'equals.wav',
            'clear.wav',
            'error.wav'
        }

        actual_files = {f.name for f in sounds_dir.glob('*.wav')}

        assert actual_files == expected_files, \
            f"Unexpected files: {actual_files - expected_files}, " \
            f"Missing files: {expected_files - actual_files}"
