"""
Unit tests for src/audio_processor.py
"""

import os
import unittest
import numpy as np
import soundfile as sf
import sys

# Add project root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.audio_processor import AudioProcessor


class TestAudioProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = AudioProcessor(target_sr=22050)
        self.test_dir = os.path.dirname(__file__)
        self.test_wav_path = os.path.join(self.test_dir, "temp_hum_test.wav")
        self.output_wav_path = os.path.join(self.test_dir, "temp_hum_processed.wav")
        
        # Create synthetic audio: 44100 Hz, stereo, 2 seconds
        # 1 sec hum tone (440 Hz A4) + 1 sec quiet noise (-80 dBFS)
        sr_input = 44100
        t = np.linspace(0, 1.0, sr_input, endpoint=False)
        hum_tone = 0.4 * np.sin(2 * np.pi * 440.0 * t)  # 440 Hz
        silence_noise = 0.0001 * np.random.randn(sr_input)  # Soft noise at -80 dBFS
        
        signal = np.concatenate([hum_tone, silence_noise])
        stereo_signal = np.column_stack([signal, signal])  # 2 channels
        
        sf.write(self.test_wav_path, stereo_signal, sr_input)

    def tearDown(self):
        for path in [self.test_wav_path, self.output_wav_path]:
            if os.path.exists(path):
                os.remove(path)

    def test_load_and_resample(self):
        audio, sr = self.processor.load_audio(self.test_wav_path)
        self.assertEqual(sr, 22050)
        self.assertEqual(audio.ndim, 1)  # Converted to mono
        self.assertAlmostEqual(len(audio), 44100, delta=100)

    def test_noise_gate(self):
        audio, sr = self.processor.load_audio(self.test_wav_path)
        gated = self.processor.apply_noise_gate(audio, threshold_db=-40.0)
        
        # Skip resample transition boundary ripple (1024 samples) and check silent region
        silent_region = gated[len(gated) // 2 + 1024:]
        self.assertTrue(np.all(silent_region == 0.0))

    def test_peak_normalization(self):
        audio, sr = self.processor.load_audio(self.test_wav_path)
        normalized = self.processor.normalize_amplitude(audio, target_db=-3.0)
        
        # Target peak amplitude for -3 dBFS is 10^(-3/20) ~ 0.707945
        expected_peak = 10 ** (-3.0 / 20.0)
        actual_peak = np.max(np.abs(normalized))
        self.assertAlmostEqual(actual_peak, expected_peak, places=3)

    def test_full_pipeline(self):
        processed_audio, sr = self.processor.preprocess(
            self.test_wav_path, 
            output_path=self.output_wav_path
        )
        self.assertEqual(sr, 22050)
        self.assertTrue(os.path.exists(self.output_wav_path))
        
        # Check generated output file properties
        info = sf.info(self.output_wav_path)
        self.assertEqual(info.samplerate, 22050)
        self.assertEqual(info.channels, 1)


if __name__ == "__main__":
    unittest.main()
