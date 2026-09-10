"""
Synthesizer & MIDI Module for Hum2Tune FYP Project.

Provides multi-instrument audio synthesis (Piano, Synth, Guitar, Flute, Strings, Chiptune)
with ADSR envelopes and exports standard MIDI (.mid) files.
"""

import os
import numpy as np
import scipy.signal
import soundfile as sf
import pretty_midi

from src.pitch_detector import PitchNote


class MusicSynthesizer:
    """Synthesizes musical notes into multi-instrument audio tracks and MIDI files."""

    INSTRUMENTS = ["Grand Piano", "Synth Lead", "Acoustic Guitar", "Flute", "Strings", "8-Bit Chiptune"]

    def __init__(self, sample_rate: int = 22050):
        self.sr = sample_rate

    @staticmethod
    def generate_adsr_envelope(
        n_samples: int,
        sr: int,
        attack_sec: float = 0.01,
        decay_sec: float = 0.05,
        sustain_level: float = 0.7,
        release_sec: float = 0.05
    ) -> np.ndarray:
        """Generate Attack-Decay-Sustain-Release (ADSR) amplitude envelope."""
        envelope = np.zeros(n_samples, dtype=np.float32)
        if n_samples == 0:
            return envelope

        a_samples = int(attack_sec * sr)
        d_samples = int(decay_sec * sr)
        r_samples = int(release_sec * sr)

        # Clamp segment lengths
        a_samples = min(a_samples, n_samples)
        d_samples = min(d_samples, max(0, n_samples - a_samples))
        r_samples = min(r_samples, max(0, n_samples - a_samples - d_samples))
        s_samples = max(0, n_samples - a_samples - d_samples - r_samples)

        curr = 0

        # Attack (0 -> 1.0)
        if a_samples > 0:
            envelope[curr:curr + a_samples] = np.linspace(0.0, 1.0, a_samples)
            curr += a_samples

        # Decay (1.0 -> sustain_level)
        if d_samples > 0:
            envelope[curr:curr + d_samples] = np.linspace(1.0, sustain_level, d_samples)
            curr += d_samples

        # Sustain
        if s_samples > 0:
            envelope[curr:curr + s_samples] = sustain_level
            curr += s_samples

        # Release (sustain_level -> 0)
        if r_samples > 0:
            envelope[curr:curr + r_samples] = np.linspace(sustain_level, 0.0, r_samples)

        return envelope

    def generate_note_waveform(
        self, 
        freq_hz: float, 
        duration_sec: float, 
        instrument: str = "Grand Piano"
    ) -> np.ndarray:
        """Synthesize waveform for a single note frequency and instrument timbre."""
        n_samples = int(duration_sec * self.sr)
        if n_samples <= 0 or freq_hz <= 0:
            return np.zeros(0, dtype=np.float32)

        t = np.linspace(0, duration_sec, n_samples, endpoint=False)

        if instrument == "8-Bit Chiptune":
            # Square wave
            raw_wave = scipy.signal.square(2 * np.pi * freq_hz * t)
            adsr = self.generate_adsr_envelope(n_samples, self.sr, 0.005, 0.02, 0.8, 0.01)

        elif instrument == "Synth Lead":
            # Sawtooth wave + harmonic
            saw = scipy.signal.sawtooth(2 * np.pi * freq_hz * t)
            sub = 0.5 * np.sin(2 * np.pi * (freq_hz / 2.0) * t)
            raw_wave = saw + sub
            adsr = self.generate_adsr_envelope(n_samples, self.sr, 0.01, 0.05, 0.7, 0.05)

        elif instrument == "Flute":
            # Soft sine wave + Vibrato LFO (5 Hz)
            vibrato = 3.0 * np.sin(2 * np.pi * 5.0 * t)
            raw_wave = np.sin(2 * np.pi * (freq_hz + vibrato) * t)
            adsr = self.generate_adsr_envelope(n_samples, self.sr, 0.08, 0.1, 0.85, 0.1)

        elif instrument == "Acoustic Guitar":
            # Plucked sine + decaying 2nd & 3rd overtones
            fundamental = np.sin(2 * np.pi * freq_hz * t)
            harm2 = 0.4 * np.sin(2 * np.pi * 2 * freq_hz * t)
            harm3 = 0.2 * np.sin(2 * np.pi * 3 * freq_hz * t)
            raw_wave = fundamental + harm2 + harm3
            adsr = self.generate_adsr_envelope(n_samples, self.sr, 0.005, 0.2, 0.3, 0.1)

        elif instrument == "Strings":
            # Rich detuned ensemble sine/saw combination
            wave1 = scipy.signal.sawtooth(2 * np.pi * freq_hz * t)
            wave2 = scipy.signal.sawtooth(2 * np.pi * (freq_hz * 1.003) * t)
            raw_wave = 0.5 * (wave1 + wave2)
            adsr = self.generate_adsr_envelope(n_samples, self.sr, 0.15, 0.1, 0.9, 0.2)

        else:  # Grand Piano (Default)
            # Warm piano sine overtones + exponential decay
            fund = np.sin(2 * np.pi * freq_hz * t)
            h2 = 0.5 * np.sin(2 * np.pi * 2 * freq_hz * t)
            h3 = 0.25 * np.sin(2 * np.pi * 3 * freq_hz * t)
            h4 = 0.125 * np.sin(2 * np.pi * 4 * freq_hz * t)
            raw_wave = fund + h2 + h3 + h4
            adsr = self.generate_adsr_envelope(n_samples, self.sr, 0.01, 0.15, 0.5, 0.15)

        synthesized = raw_wave * adsr
        return synthesized.astype(np.float32)

    def synthesize_tune(
        self, 
        notes: list[PitchNote], 
        instrument: str = "Grand Piano", 
        output_path: str = None
    ) -> np.ndarray:
        """Render list of PitchNotes into a single mixed audio waveform."""
        if not notes:
            return np.zeros(self.sr, dtype=np.float32)  # 1 sec silence

        # Total audio length in seconds
        max_end_time = max(n.end_time for n in notes) + 0.5
        total_samples = int(max_end_time * self.sr)
        audio_buffer = np.zeros(total_samples, dtype=np.float32)

        for note in notes:
            note_audio = self.generate_note_waveform(
                freq_hz=note.frequency_hz,
                duration_sec=note.duration,
                instrument=instrument
            )
            start_sample = int(note.start_time * self.sr)
            end_sample = start_sample + len(note_audio)

            if end_sample > total_samples:
                # Extend buffer if needed
                extension = end_sample - total_samples
                audio_buffer = np.pad(audio_buffer, (0, extension))
                total_samples = len(audio_buffer)

            audio_buffer[start_sample:end_sample] += note_audio * note.velocity

        # Normalize total audio output to prevent clipping distortion
        peak = np.max(np.abs(audio_buffer))
        if peak > 0:
            audio_buffer = (audio_buffer / peak) * 0.85

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            sf.write(output_path, audio_buffer, self.sr)

        return audio_buffer

    def export_midi(self, notes: list[PitchNote], output_path: str, bpm: int = 120) -> str:
        """Export list of PitchNotes as a standard downloadable .mid MIDI file."""
        midi_data = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        # Program 0 is Acoustic Grand Piano
        instrument_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
        midi_instrument = pretty_midi.Instrument(program=instrument_program)

        for note in notes:
            pm_note = pretty_midi.Note(
                velocity=int(note.velocity * 127),
                pitch=note.pitch_midi,
                start=note.start_time,
                end=note.end_time
            )
            midi_instrument.notes.append(pm_note)

        midi_data.instruments.append(midi_instrument)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        midi_data.write(output_path)
        return output_path
