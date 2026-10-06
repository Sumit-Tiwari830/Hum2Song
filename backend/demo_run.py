"""
Demo Execution Script for Hum2Tune FYP Project.

Generates a realistic dummy humming recording, runs the complete pipeline
(Preprocessing -> Pitch Detection -> RAG Harmony Retrieval -> Audio Synth & MIDI Export),
and outputs the generated files for testing.
"""

import os
import sys
import numpy as np
import soundfile as sf

# Add project root directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.audio_processor import AudioProcessor
from src.pitch_detector import PitchDetector
from src.synthesizer import MusicSynthesizer
from src.harmony_rag import MusicHarmonyRAG


def create_dummy_humming_wav(output_path: str, sr: int = 22050) -> str:
    """
    Generate a 3.5-second realistic dummy humming WAV file.
    Melody: E4 (329.63Hz) -> D4 (293.66Hz) -> C4 (261.63Hz) -> D4 (293.66Hz) -> E4 (329.63Hz)
    Includes warm vocal vocalization overtones (2nd/3rd harmonics) + breath noise.
    """
    notes_sequence = [
        (329.63, 0.6),  # E4
        (293.66, 0.6),  # D4
        (261.63, 0.6),  # C4
        (293.66, 0.6),  # D4
        (329.63, 0.8),  # E4
    ]

    audio_segments = []
    for freq, duration in notes_sequence:
        n_samples = int(duration * sr)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Vocal hum timbre: Fundamental + warm 2nd/3rd overtones + slight vibrato
        vibrato = 2.0 * np.sin(2 * np.pi * 5.5 * t)
        f0 = freq + vibrato
        fund = 0.5 * np.sin(2 * np.pi * f0 * t)
        harm2 = 0.25 * np.sin(2 * np.pi * 2 * f0 * t)
        harm3 = 0.1 * np.sin(2 * np.pi * 3 * f0 * t)
        raw_hum = fund + harm2 + harm3

        # Smooth vocal onset and offset envelope (fade in / out)
        env = np.ones(n_samples)
        fade_len = int(0.05 * sr)
        env[:fade_len] = np.linspace(0, 1, fade_len)
        env[-fade_len:] = np.linspace(1, 0, fade_len)

        hum_note = raw_hum * env
        audio_segments.append(hum_note)

        # Brief silence gap between hummed notes
        gap = np.zeros(int(0.08 * sr))
        audio_segments.append(gap)

    full_humming = np.concatenate(audio_segments)
    # Add subtle background air noise (-50 dBFS)
    noise = 0.003 * np.random.randn(len(full_humming))
    full_humming += noise

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, full_humming.astype(np.float32), sr)
    return output_path


def main():
    print("=" * 70)
    print("🎵 HUM2TUNE: DEMO HUMMING-TO-TUNE PIPELINE TEST")
    print("=" * 70)

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    dummy_input_path = os.path.join(output_dir, "dummy_humming_recording.wav")
    synthesized_wav_path = os.path.join(output_dir, "demo_synthesized_tune.wav")
    midi_output_path = os.path.join(output_dir, "demo_tune.mid")

    # Step 1: Create Dummy Humming Recording
    print("\n1. 🎤 Generating realistic dummy humming audio recording...")
    create_dummy_humming_wav(dummy_input_path)
    print(f"   Saved input recording to: {dummy_input_path}")

    # Step 2: Preprocess Audio Signal
    print("\n2. 🧹 Preprocessing humming audio (Noise Gate & Peak Normalization)...")
    processor = AudioProcessor(target_sr=22050)
    clean_audio, sr = processor.preprocess(dummy_input_path)
    print(f"   Cleaned audio length: {len(clean_audio)/sr:.2f} seconds | Sample Rate: {sr} Hz")

    # Step 3: Detect Pitches & Notes
    print("\n3. 🧠 Detecting musical note pitches (pYIN pitch tracking)...")
    pitch_detector = PitchDetector()
    notes = pitch_detector.detect_notes_pyin(clean_audio, sr=sr)
    print(f"   Detected {len(notes)} musical note events:")
    for idx, n in enumerate(notes, 1):
        print(f"   Note #{idx}: {n.pitch_name:<4} (MIDI {n.pitch_midi}) | Pitch: {n.frequency_hz:.1f} Hz | Time: {n.start_time:.2f}s - {n.end_time:.2f}s")

    # Step 4: Query Music Harmony RAG Engine
    print("\n4. 🔍 Querying Music Harmony RAG Vector DB for matching chords...")
    rag = MusicHarmonyRAG()
    matches = rag.retrieve_best_harmony(notes, top_k=1)

    if matches:
        top_match = matches[0]
        print(f"   RAG Harmony Match Found!")
        print(f"   - Genre / Style : {top_match.genre}")
        print(f"   - Key Signature  : {top_match.key_name}")
        print(f"   - Backing Chords : {', '.join(top_match.chord_names)}")
        print(f"   - Match Confidence: {top_match.similarity_score * 100:.1f}%")
        print(f"   - Description    : {top_match.description}")
    else:
        top_match = None

    # Step 5: Synthesize Instrument Track + RAG Backing Band
    print("\n5. 🎹 Synthesizing Multi-Instrument Audio (Grand Piano + Acoustic Guitar Backing)...")
    synth = MusicSynthesizer(sample_rate=22050)
    lead_tune = synth.synthesize_tune(notes, instrument="Grand Piano")

    if top_match:
        total_duration = max(n.end_time for n in notes)
        backing_band = rag.generate_backing_band(
            harmony=top_match,
            duration_sec=total_duration,
            synth=synth,
            instrument="Acoustic Guitar"
        )

        # Mix Lead Piano + Backing Guitar
        max_len = max(len(lead_tune), len(backing_band))
        mixed = np.zeros(max_len, dtype=np.float32)
        mixed[:len(lead_tune)] += lead_tune * 0.8
        mixed[:len(backing_band)] += backing_band * 0.45
        final_audio = (mixed / (np.max(np.abs(mixed)) + 1e-6)) * 0.85
    else:
        final_audio = lead_tune

    sf.write(synthesized_wav_path, final_audio, sr)
    print(f"   Synthesized Audio saved to: {synthesized_wav_path}")

    # Step 6: Export MIDI File
    print("\n6. 💾 Exporting Standard MIDI (.mid) file...")
    synth.export_midi(notes, midi_output_path)
    print(f"   MIDI Track saved to: {midi_output_path}")

    print("\n" + "=" * 70)
    print("✨ DEMO TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
