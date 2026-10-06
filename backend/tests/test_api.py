"""
Unit tests for main.py (FastAPI Server)
"""

import os
import unittest
import numpy as np
import soundfile as sf
import sys
from fastapi.testclient import TestClient

# Add project root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app


class TestFastAPIBackend(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.test_dir = os.path.dirname(__file__)
        self.test_audio_path = os.path.join(self.test_dir, "temp_api_hum.wav")

        # Create 1-second sample audio file (A4 440 Hz)
        sr = 22050
        t = np.linspace(0, 1.0, sr, endpoint=False)
        audio = 0.5 * np.sin(2 * np.pi * 440.0 * t)
        sf.write(self.test_audio_path, audio, sr)

    def tearDown(self):
        if os.path.exists(self.test_audio_path):
            os.remove(self.test_audio_path)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_get_instruments(self):
        response = self.client.get("/api/instruments")
        self.assertEqual(response.status_code, 200)
        instruments = response.json()["instruments"]
        self.assertIn("Grand Piano", instruments)

    def test_process_humming_endpoint(self):
        with open(self.test_audio_path, "rb") as f:
            files = {"file": ("test_hum.wav", f, "audio/wav")}
            data = {"instrument": "Grand Piano", "enable_rag_backing": "true"}
            response = self.client.post("/api/process-humming", files=files, data=data)

        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertIn("session_id", res_json)
        self.assertGreater(res_json["num_notes_detected"], 0)
        self.assertTrue(res_json["synthesized_audio_url"].startswith("/api/download/"))
        self.assertTrue(res_json["midi_file_url"].startswith("/api/download/"))
        self.assertIn("genre", res_json["rag_harmony"])

        # Test download endpoint for the generated WAV file
        wav_url = res_json["synthesized_audio_url"]
        dl_response = self.client.get(wav_url)
        self.assertEqual(dl_response.status_code, 200)
        self.assertEqual(dl_response.headers["content-type"], "audio/wav")


if __name__ == "__main__":
    unittest.main()
