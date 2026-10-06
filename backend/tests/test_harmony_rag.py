"""
Unit tests for src/harmony_rag.py
"""

import os
import unittest
import numpy as np
import sys

# Add project root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pitch_detector import PitchNote
from src.synthesizer import MusicSynthesizer
from src.harmony_rag import MusicHarmonyRAG, HarmonyMatch


class TestMusicHarmonyRAG(unittest.TestCase):

    def setUp(self):
        self.rag = MusicHarmonyRAG()
        self.synth = MusicSynthesizer(sample_rate=22050)

        # Sample pitch notes (Melody: C4 -> E4 -> G4 -> A4)
        self.sample_notes = [
            PitchNote(pitch_midi=60, pitch_name="C4", frequency_hz=261.63, start_time=0.0, end_time=0.5),
            PitchNote(pitch_midi=64, pitch_name="E4", frequency_hz=329.63, start_time=0.5, end_time=1.0),
            PitchNote(pitch_midi=67, pitch_name="G4", frequency_hz=392.00, start_time=1.0, end_time=1.5),
            PitchNote(pitch_midi=69, pitch_name="A4", frequency_hz=440.00, start_time=1.5, end_time=2.0),
        ]

    def test_vector_retrieval(self):
        matches = self.rag.retrieve_best_harmony(self.sample_notes, top_k=1)
        self.assertEqual(len(matches), 1)
        match = matches[0]
        self.assertIsInstance(match, HarmonyMatch)
        self.assertTrue(len(match.genre) > 0)
        self.assertTrue(len(match.chord_names) > 0)
        self.assertGreater(match.similarity_score, 0.0)

    def test_backing_band_synthesis(self):
        matches = self.rag.retrieve_best_harmony(self.sample_notes, top_k=1)
        match = matches[0]
        backing_audio = self.rag.generate_backing_band(
            harmony=match,
            duration_sec=2.0,
            synth=self.synth,
            instrument="Acoustic Guitar"
        )
        self.assertGreater(len(backing_audio), 0)
        self.assertFalse(np.all(backing_audio == 0.0))


if __name__ == "__main__":
    unittest.main()
