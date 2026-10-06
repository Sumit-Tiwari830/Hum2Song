"""
Unit tests for src/synthesizer.py
"""

import os
import unittest
import numpy as np
import pretty_midi
import soundfile as sf
import sys

# Add project root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pitch_detector import PitchNote
from src.synthesizer import MusicSynthesizer


class TestMusicSynthesizer(unittest.TestCase):

    def setUp(self):
        self.synth = MusicSynthesizer(sample_rate=22050)
        self.test_dir = os.path.dirname(__file__)
        self.midi_path = os.path.join(self.test_dir, "temp_tune.mid")
        self.wav_path = os.path.join(self.test_dir, "temp_tune.wav")

        # Create sample PitchNotes (A4 and C5)
        self.sample_notes = [
            PitchNote(pitch_midi=69, pitch_name="A4", frequency_hz=440.0, start_time=0.0, end_time=0.5, velocity=0.8),
            PitchNote(pitch_midi=72, pitch_name="C5", frequency_hz=523.25, start_time=0.6, end_time=1.1, velocity=0.8)
        ]

    def tearDown(self):
        for path in [self.midi_path, self.wav_path]:
            if os.path.exists(path):
                os.remove(path)

    def test_all_instruments_synthesis(self):
        for inst in MusicSynthesizer.INSTRUMENTS:
            audio = self.synth.synthesize_tune(self.sample_notes, instrument=inst)
            self.assertGreater(len(audio), 0)
            self.assertFalse(np.all(audio == 0.0))
            # Verify no NaN or Inf
            self.assertFalse(np.isnan(audio).any())
            self.assertFalse(np.isinf(audio).any())

    def test_export_wav(self):
        audio = self.synth.synthesize_tune(self.sample_notes, instrument="Grand Piano", output_path=self.wav_path)
        self.assertTrue(os.path.exists(self.wav_path))
        info = sf.info(self.wav_path)
        self.assertEqual(info.samplerate, 22050)

    def test_export_midi(self):
        self.synth.export_midi(self.sample_notes, self.midi_path, bpm=120)
        self.assertTrue(os.path.exists(self.midi_path))
        
        # Read back MIDI file with pretty_midi to verify integrity
        pm = pretty_midi.PrettyMIDI(self.midi_path)
        self.assertEqual(len(pm.instruments), 1)
        inst_notes = pm.instruments[0].notes
        self.assertEqual(len(inst_notes), 2)
        self.assertEqual(inst_notes[0].pitch, 69)
        self.assertEqual(inst_notes[1].pitch, 72)


if __name__ == "__main__":
    unittest.main()
