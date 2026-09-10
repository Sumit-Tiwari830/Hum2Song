"""
FastAPI Backend Server for Hum2Tune FYP Project.

Provides REST API endpoints for uploading humming audio recordings, 
detecting pitches, querying Music RAG harmonies, synthesizing instrument tunes, 
and downloading MIDI & WAV files.
"""

import os
import uuid
import numpy as np
import soundfile as sf
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.audio_processor import AudioProcessor
from src.pitch_detector import PitchDetector, PitchNote
from src.synthesizer import MusicSynthesizer
from src.harmony_rag import MusicHarmonyRAG, HarmonyMatch

app = FastAPI(
    title="Hum2Tune API",
    description="AI-Powered Humming-to-Music Synthesizer & RAG Harmony API",
    version="1.0.0"
)

# Enable CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directories for saving outputs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize core engines
processor = AudioProcessor(target_sr=22050)
pitch_detector = PitchDetector()
synthesizer = MusicSynthesizer(sample_rate=22050)
rag_engine = MusicHarmonyRAG(db_dir=os.path.join(BASE_DIR, "chroma_db"))


class PitchNoteResponse(BaseModel):
    pitch_midi: int
    pitch_name: str
    frequency_hz: float
    start_time: float
    end_time: float
    duration: float


class ProcessHummingResponse(BaseModel):
    session_id: str
    num_notes_detected: int
    notes: list[PitchNoteResponse]
    synthesized_audio_url: str
    midi_file_url: str
    rag_harmony: dict


@app.get("/health")
def health_check():
    """Server health check endpoint."""
    return {"status": "ok", "service": "Hum2Tune API"}


@app.get("/api/instruments")
def get_instruments():
    """Return available synth instruments."""
    return {"instruments": MusicSynthesizer.INSTRUMENTS}


@app.post("/api/process-humming", response_model=ProcessHummingResponse)
async def process_humming(
    file: UploadFile = File(...),
    instrument: str = Form("Grand Piano"),
    enable_rag_backing: bool = Form(True)
):
    """
    Upload a humming audio file, extract pitch notes, query RAG harmony, 
    synthesize instrument track, and return downloadable URLs.
    """
    session_id = str(uuid.uuid4())[:8]
    temp_input_path = os.path.join(OUTPUT_DIR, f"input_{session_id}_{file.filename}")

    try:
        # Save uploaded file
        with open(temp_input_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 1. Preprocess Audio
        preprocessed_audio, sr = processor.preprocess(temp_input_path)

        # 2. Extract Pitch Notes using pYIN
        notes = pitch_detector.detect_notes_pyin(preprocessed_audio, sr=sr)

        if not notes:
            # Fallback default note if no pitch detected in silent audio
            notes = [PitchNote(pitch_midi=60, pitch_name="C4", frequency_hz=261.63, start_time=0.0, end_time=1.0)]

        # 3. Query RAG Harmony Engine
        rag_matches = rag_engine.retrieve_best_harmony(notes, top_k=1)
        top_harmony = rag_matches[0] if rag_matches else None

        # 4. Synthesize Audio Tune
        tune_audio = synthesizer.synthesize_tune(notes, instrument=instrument)

        # If RAG backing requested, mix backing band with lead tune
        if enable_rag_backing and top_harmony:
            total_dur = max(n.end_time for n in notes)
            backing_audio = rag_engine.generate_backing_band(
                harmony=top_harmony,
                duration_sec=total_dur,
                synth=synthesizer,
                instrument="Acoustic Guitar"
            )

            # Match lengths and mix lead + backing
            max_len = max(len(tune_audio), len(backing_audio))
            mixed = np.zeros(max_len, dtype=np.float32)
            mixed[:len(tune_audio)] += tune_audio * 0.8
            mixed[:len(backing_audio)] += backing_audio * 0.4
            tune_audio = mixed / (np.max(np.abs(mixed)) + 1e-6) * 0.85

        # Save output WAV audio file
        wav_filename = f"tune_{session_id}.wav"
        wav_output_path = os.path.join(OUTPUT_DIR, wav_filename)
        sf.write(wav_output_path, tune_audio, sr)

        # 5. Export MIDI file
        midi_filename = f"tune_{session_id}.mid"
        midi_output_path = os.path.join(OUTPUT_DIR, midi_filename)
        synthesizer.export_midi(notes, midi_output_path)

        # Build response
        notes_resp = [
            PitchNoteResponse(
                pitch_midi=n.pitch_midi,
                pitch_name=n.pitch_name,
                frequency_hz=round(n.frequency_hz, 2),
                start_time=round(n.start_time, 2),
                end_time=round(n.end_time, 2),
                duration=round(n.duration, 2)
            ) for n in notes
        ]

        rag_resp = {
            "genre": top_harmony.genre if top_harmony else "N/A",
            "key_name": top_harmony.key_name if top_harmony else "N/A",
            "chord_names": top_harmony.chord_names if top_harmony else [],
            "description": top_harmony.description if top_harmony else "N/A",
            "similarity_score": round(top_harmony.similarity_score, 3) if top_harmony else 0.0
        }

        return ProcessHummingResponse(
            session_id=session_id,
            num_notes_detected=len(notes),
            notes=notes_resp,
            synthesized_audio_url=f"/api/download/{wav_filename}",
            midi_file_url=f"/api/download/{midi_filename}",
            rag_harmony=rag_resp
        )

    finally:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)


@app.get("/api/download/{filename}")
def download_file(filename: str):
    """Download synthesized WAV audio or MIDI file."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    media_type = "audio/wav" if filename.endswith(".wav") else "audio/midi"
    return FileResponse(file_path, media_type=media_type, filename=filename)
