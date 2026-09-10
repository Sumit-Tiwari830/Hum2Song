"""
Pitch Detector Module for Hum2Tune FYP Project.

Extracts musical note events, onset/offset times, pitch frequencies, 
and MIDI note numbers from human humming audio signals using 
Signal Processing (pYIN) and AI Pitch Estimation.
"""

from dataclasses import dataclass
import numpy as np
import librosa


@dataclass
class PitchNote:
    """Represents a detected musical note event from humming audio."""
    pitch_midi: int
    pitch_name: str
    frequency_hz: float
    start_time: float
    end_time: float
    velocity: float = 0.8

    @property
    def duration(self) -> float:
        """Note duration in seconds."""
        return max(0.0, self.end_time - self.start_time)


class PitchDetector:
    """Detects musical pitches and converts audio signals into structured note sequences."""

    NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def __init__(self, min_freq: float = 65.0, max_freq: float = 1046.5):
        """
        Initialize PitchDetector.
        
        Args:
            min_freq (float): Minimum pitch frequency to track (C2 ~ 65 Hz).
            max_freq (float): Maximum pitch frequency to track (C6 ~ 1046.5 Hz).
        """
        self.min_freq = min_freq
        self.max_freq = max_freq

    @classmethod
    def hz_to_midi(cls, freq_hz: float) -> int:
        """Convert pitch frequency in Hz to nearest MIDI note number."""
        if freq_hz <= 0 or np.isnan(freq_hz):
            return 0
        return int(round(69 + 12 * np.log2(freq_hz / 440.0)))

    @classmethod
    def midi_to_note_name(cls, midi_num: int) -> str:
        """Convert MIDI note number (0-127) to standard note name string (e.g. 'A4', 'C#5')."""
        if midi_num <= 0 or midi_num > 127:
            return "N/A"
        octave = (midi_num // 12) - 1
        note_idx = midi_num % 12
        return f"{cls.NOTE_NAMES[note_idx]}{octave}"

    @classmethod
    def midi_to_hz(cls, midi_num: int) -> float:
        """Convert MIDI note number to frequency in Hz."""
        return 440.0 * (2.0 ** ((midi_num - 69) / 12.0))

    def detect_notes_pyin(
        self, 
        audio: np.ndarray, 
        sr: int = 22050, 
        frame_length: int = 2048, 
        hop_length: int = 512,
        min_note_duration: float = 0.08
    ) -> list[PitchNote]:
        """
        Extract note events from audio array using Probabilistic YIN (pYIN) pitch tracking.
        
        Args:
            audio (np.ndarray): Preprocessed 1D mono float32 audio signal.
            sr (int): Sample rate (default 22050 Hz).
            frame_length (int): Frame length for STFT/pYIN analysis.
            hop_length (int): Hop length between frames.
            min_note_duration (float): Minimum duration (seconds) to retain a note.
            
        Returns:
            list[PitchNote]: List of detected note events sorted by start time.
        """
        if len(audio) == 0:
            return []

        # Run Librosa pYIN fundamental frequency estimation
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=self.min_freq,
            fmax=self.max_freq,
            sr=sr,
            frame_length=frame_length,
            hop_length=hop_length
        )

        times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop_length)

        notes: list[PitchNote] = []
        current_midi = None
        start_t = 0.0
        pitch_buffer = []

        for i in range(len(f0)):
            freq = f0[i]
            is_voiced = voiced_flag[i] and not np.isnan(freq) and freq > 0

            if is_voiced:
                midi_val = self.hz_to_midi(freq)
                if current_midi is None:
                    current_midi = midi_val
                    start_t = times[i]
                    pitch_buffer = [freq]
                elif midi_val == current_midi:
                    pitch_buffer.append(freq)
                else:
                    # Pitch change: finalize previous note
                    end_t = times[i]
                    if (end_t - start_t) >= min_note_duration:
                        avg_hz = float(np.mean(pitch_buffer))
                        notes.append(PitchNote(
                            pitch_midi=current_midi,
                            pitch_name=self.midi_to_note_name(current_midi),
                            frequency_hz=avg_hz,
                            start_time=float(start_t),
                            end_time=float(end_t),
                            velocity=0.8
                        ))
                    current_midi = midi_val
                    start_t = times[i]
                    pitch_buffer = [freq]
            else:
                if current_midi is not None:
                    end_t = times[i]
                    if (end_t - start_t) >= min_note_duration:
                        avg_hz = float(np.mean(pitch_buffer))
                        notes.append(PitchNote(
                            pitch_midi=current_midi,
                            pitch_name=self.midi_to_note_name(current_midi),
                            frequency_hz=avg_hz,
                            start_time=float(start_t),
                            end_time=float(end_t),
                            velocity=0.8
                        ))
                    current_midi = None
                    pitch_buffer = []

        # Flush final note if trailing active
        if current_midi is not None and len(times) > 0:
            end_t = times[-1]
            if (end_t - start_t) >= min_note_duration:
                avg_hz = float(np.mean(pitch_buffer))
                notes.append(PitchNote(
                    pitch_midi=current_midi,
                    pitch_name=self.midi_to_note_name(current_midi),
                    frequency_hz=avg_hz,
                    start_time=float(start_t),
                    end_time=float(end_t),
                    velocity=0.8
                ))

        return notes
