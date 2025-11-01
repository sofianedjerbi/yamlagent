#!/usr/bin/env python3
"""
Test script to verify audio files are valid WAV files.

Checks that all sound files:
- Exist
- Are valid WAV format
- Have reasonable size and duration
- Have correct audio properties
"""

import wave
from pathlib import Path


def test_wav_file(filepath: Path) -> dict:
    """
    Test a WAV file and return its properties.

    Args:
        filepath: Path to WAV file

    Returns:
        Dictionary with file properties
    """
    try:
        with wave.open(str(filepath), 'rb') as wav:
            properties = {
                'exists': True,
                'channels': wav.getnchannels(),
                'sample_width': wav.getsampwidth(),
                'framerate': wav.getframerate(),
                'frames': wav.getnframes(),
                'duration': wav.getnframes() / wav.getframerate(),
                'size': filepath.stat().st_size,
                'valid': True,
                'error': None
            }
        return properties
    except Exception as e:
        return {
            'exists': filepath.exists(),
            'valid': False,
            'error': str(e)
        }


def main():
    """Run audio file tests."""
    print("=" * 70)
    print("Calc3D Audio File Test")
    print("=" * 70)
    print()

    sounds_dir = Path(__file__).parent / "src" / "calc3d" / "static" / "sounds"

    if not sounds_dir.exists():
        print(f"❌ Sounds directory not found: {sounds_dir}")
        return 1

    # Expected sound files
    sound_files = {
        'digit.wav': {'min_duration': 0.04, 'max_duration': 0.06},
        'operator.wav': {'min_duration': 0.07, 'max_duration': 0.09},
        'equals.wav': {'min_duration': 0.14, 'max_duration': 0.16},
        'clear.wav': {'min_duration': 0.14, 'max_duration': 0.16},
        'error.wav': {'min_duration': 0.19, 'max_duration': 0.21},
    }

    all_valid = True

    for filename, expected in sound_files.items():
        filepath = sounds_dir / filename
        print(f"Testing {filename}...")

        props = test_wav_file(filepath)

        if not props.get('exists'):
            print(f"  ❌ File does not exist")
            all_valid = False
            continue

        if not props.get('valid'):
            print(f"  ❌ Invalid WAV file: {props.get('error')}")
            all_valid = False
            continue

        # Check properties
        checks = []

        # Mono audio
        if props['channels'] == 1:
            checks.append("✓ Mono")
        else:
            checks.append(f"✗ {props['channels']} channels (expected 1)")
            all_valid = False

        # 16-bit audio
        if props['sample_width'] == 2:
            checks.append("✓ 16-bit")
        else:
            checks.append(f"✗ {props['sample_width']*8}-bit (expected 16)")
            all_valid = False

        # 44.1 kHz sample rate
        if props['framerate'] == 44100:
            checks.append("✓ 44.1 kHz")
        else:
            checks.append(f"✗ {props['framerate']} Hz (expected 44100)")
            all_valid = False

        # Duration in expected range
        duration = props['duration']
        if expected['min_duration'] <= duration <= expected['max_duration']:
            checks.append(f"✓ {duration:.3f}s")
        else:
            checks.append(f"✗ {duration:.3f}s (expected {expected['min_duration']}-{expected['max_duration']})")
            all_valid = False

        # Reasonable file size (> 1KB)
        size_kb = props['size'] / 1024
        if props['size'] > 1000:
            checks.append(f"✓ {size_kb:.1f} KB")
        else:
            checks.append(f"✗ {size_kb:.1f} KB (too small)")
            all_valid = False

        # Print results
        for check in checks:
            print(f"  {check}")

        print()

    print("=" * 70)
    if all_valid:
        print("✅ All audio files are valid!")
        return 0
    else:
        print("❌ Some audio files have issues")
        return 1


if __name__ == "__main__":
    exit(main())
