"""
Unit tests for src/pitch_detector.py
"""

import os
import unittest
import numpy as np
import sys

# Add project root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pitch_detector import PitchDetector, PitchNote


class TestPitchDetector(unittest.TestCase):

    def setUp(self):
        self.detector = PitchDetector()

    def test_hz_midi_conversions(self):
        # Test A4 (440 Hz -> MIDI 69)
        self.assertEqual(PitchDetector.hz_to_midi(440.0), 69)
        self.assertEqual(PitchDetector.midi_to_note_name(69), "A4")
        self.assertAlmostEqual(PitchDetector.midi_to_hz(69), 440.0, places=2)

        # Test Middle C (261.63 Hz -> MIDI 60)
        self.assertEqual(PitchDetector.hz_to_midi(261.63), 60)
        self.assertEqual(PitchDetector.midi_to_note_name(60), "C4")

    def test_detect_notes_pyin(self):
        sr = 22050
        duration_per_note = 0.5
        t = np.linspace(0, duration_per_note, int(sr * duration_per_note), endpoint=False)

        # Note 1: 440 Hz (A4 / MIDI 69)
        note1_audio = 0.5 * np.sin(2 * np.pi * 440.0 * t)
        # Silence gap
        silence = np.zeros(int(sr * 0.1))
        # Note 2: 523.25 Hz (C5 / MIDI 72)
        note2_audio = 0.5 * np.sin(2 * np.pi * 523.25 * t)

        audio_signal = np.concatenate([note1_audio, silence, note2_audio])

        notes = self.detector.detect_notes_pyin(audio_signal, sr=sr)

        # Verify notes detected
        self.assertGreaterEqual(len(notes), 2)
        
        # Check first note detected is A4 (MIDI 69)
        self.assertEqual(notes[0].pitch_midi, 69)
        self.assertEqual(notes[0].pitch_name, "A4")

        # Check second note detected is C5 (MIDI 72)
        self.assertEqual(notes[-1].pitch_midi, 72)
        self.assertEqual(notes[-1].pitch_name, "C5")


if __name__ == "__main__":
    unittest.main()
