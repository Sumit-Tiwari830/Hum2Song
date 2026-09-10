"""
Audio Preprocessor Module for Hum2Tune FYP Project.

Provides signal processing utilities for loading, resampling, noise gating, 
and amplitude normalization of human humming audio inputs.
"""

import os
import numpy as np
import scipy.signal
import soundfile as sf


class AudioProcessor:
    """Preprocesses raw audio humming recordings for AI pitch extraction."""

    def __init__(self, target_sr: int = 22050):
        """
        Initialize AudioProcessor.
        
        Args:
            target_sr (int): Target sampling rate in Hz (default 22050 Hz).
        """
        self.target_sr = target_sr

    def load_audio(self, file_path: str) -> tuple[np.ndarray, int]:
        """
        Load audio file, convert to mono channel, and resample to target sampling rate.
        
        Args:
            file_path (str): Path to input audio file (.wav, .mp3, .flac, .ogg).
            
        Returns:
            tuple[np.ndarray, int]: (mono_audio_array, target_sample_rate)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Read audio using soundfile
        audio, sr = sf.read(file_path)

        # Convert stereo or multi-channel to mono by averaging channels
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)

        # Ensure float32 dtype
        audio = audio.astype(np.float32)

        # Resample if current sample rate differs from target sample rate
        if sr != self.target_sr:
            num_samples = int(round(len(audio) * float(self.target_sr) / sr))
            audio = scipy.signal.resample(audio, num_samples)
            sr = self.target_sr

        return audio, sr

    def apply_noise_gate(self, audio: np.ndarray, threshold_db: float = -40.0) -> np.ndarray:
        """
        Suppress silent or background noise frames below a threshold dB level.
        
        Args:
            audio (np.ndarray): 1D float32 audio signal array.
            threshold_db (float): Silence threshold in decibels relative to full scale (dBFS).
            
        Returns:
            np.ndarray: Gated audio signal array.
        """
        if len(audio) == 0:
            return audio

        # Linear amplitude threshold derived from dBFS: threshold_lin = 10^(dB / 20)
        threshold_lin = 10.0 ** (threshold_db / 20.0)

        # Compute rolling RMS energy frame by frame
        frame_size = 512
        gated_audio = audio.copy()
        n_samples = len(audio)

        for start in range(0, n_samples, frame_size):
            end = min(start + frame_size, n_samples)
            frame = audio[start:end]
            frame_rms = np.sqrt(np.mean(frame ** 2) + 1e-12)

            if frame_rms < threshold_lin:
                gated_audio[start:end] = 0.0

        return gated_audio

    def normalize_amplitude(self, audio: np.ndarray, target_db: float = -3.0) -> np.ndarray:
        """
        Peak normalize audio signal to a target dBFS peak amplitude level.
        
        Args:
            audio (np.ndarray): 1D audio signal array.
            target_db (float): Peak target amplitude in dB (default -3.0 dB).
            
        Returns:
            np.ndarray: Amplitude-normalized audio signal array.
        """
        peak = np.max(np.abs(audio))
        if peak == 0 or np.isnan(peak):
            return audio

        target_peak = 10.0 ** (target_db / 20.0)
        scaling_factor = target_peak / peak
        normalized_audio = audio * scaling_factor

        return normalized_audio.astype(np.float32)

    def preprocess(
        self, 
        input_path: str, 
        output_path: str = None, 
        threshold_db: float = -40.0, 
        target_db: float = -3.0
    ) -> tuple[np.ndarray, int]:
        """
        Full audio preprocessing pipeline: Load -> Mono -> Resample -> Noise Gate -> Peak Normalize.
        
        Args:
            input_path (str): Input audio file path.
            output_path (str, optional): Save preprocessed audio to disk if specified.
            threshold_db (float): Noise gate threshold dB.
            target_db (float): Peak normalization dB.
            
        Returns:
            tuple[np.ndarray, int]: (preprocessed_audio_array, sample_rate)
        """
        audio, sr = self.load_audio(input_path)
        gated_audio = self.apply_noise_gate(audio, threshold_db=threshold_db)
        normalized_audio = self.normalize_amplitude(gated_audio, target_db=target_db)

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            sf.write(output_path, normalized_audio, sr)

        return normalized_audio, sr
