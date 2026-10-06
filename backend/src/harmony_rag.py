"""
Music Harmony RAG (Retrieval-Augmented Generation) Engine for Hum2Tune FYP Project.

Indexes musical chord progressions, scale structures, and genre templates into ChromaDB.
Retrieves matching backing harmonies for a hummed melody based on pitch vector embeddings.
"""

import os
from dataclasses import dataclass
import numpy as np
import chromadb
from chromadb.config import Settings

from src.pitch_detector import PitchNote, PitchDetector
from src.synthesizer import MusicSynthesizer


@dataclass
class HarmonyMatch:
    """Represents a retrieved harmony progression from the Vector DB."""
    genre: str
    key_name: str
    chord_names: list[str]
    chord_midis: list[list[int]]  # Polyphonic MIDI note numbers for each chord
    similarity_score: float
    description: str


class MusicHarmonyRAG:
    """RAG system for audio melody matching & automatic chord progression generation."""

    HARMONY_KNOWLEDGE_BASE = [
        {
            "id": "pop_major_1",
            "genre": "Pop / Bright",
            "key_name": "C Major",
            "chord_names": ["C", "G", "Am", "F"],
            "chord_midis": [[48, 52, 55], [43, 47, 50], [45, 48, 52], [41, 45, 48]], # Bass + triad
            "contour": [0, 4, 7, 2, -2, 5, 0],
            "description": "Upbeat classic I-V-vi-IV pop progression."
        },
        {
            "id": "pop_minor_1",
            "genre": "Emotional Pop",
            "key_name": "A Minor",
            "chord_names": ["Am", "F", "C", "G"],
            "chord_midis": [[45, 48, 52], [41, 45, 48], [48, 52, 55], [43, 47, 50]],
            "contour": [0, -3, 3, 2, -5, 0],
            "description": "Emotional i-VI-III-VII minor progression."
        },
        {
            "id": "jazz_lofi_1",
            "genre": "Jazz / Lofi",
            "key_name": "C Major 7",
            "chord_names": ["Dm7", "G7", "Cmaj7", "A7"],
            "chord_midis": [[50, 53, 57, 60], [43, 47, 50, 53], [48, 52, 55, 59], [45, 49, 52, 55]],
            "contour": [2, 5, -1, 4, 0, 7],
            "description": "Sophisticated ii-V-I jazz turnaround."
        },
        {
            "id": "rock_blues_1",
            "genre": "Rock / Blues",
            "key_name": "E Blues",
            "chord_names": ["E", "A", "E", "B7"],
            "chord_midis": [[40, 44, 47], [45, 49, 52], [40, 44, 47], [47, 51, 54, 57]],
            "contour": [0, 5, 0, 7, -3, 2],
            "description": "Driving 12-bar blues I-IV-V progression."
        },
        {
            "id": "cinematic_epic_1",
            "genre": "Cinematic / Epic",
            "key_name": "A Minor Epic",
            "chord_names": ["Am", "F", "Dm", "E7"],
            "chord_midis": [[45, 48, 52], [41, 45, 48], [50, 53, 57], [40, 44, 47, 50]],
            "contour": [0, -4, 2, 6, -2, 0],
            "description": "Dramatic orchestral minor progression."
        }
    ]

    def __init__(self, db_dir: str = None):
        """Initialize ChromaDB vector database and populate harmony knowledge base."""
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=db_dir)
        else:
            self.client = chromadb.Client(Settings(is_persistent=False))

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="music_harmonies",
            metadata={"hnsw:space": "cosine"}
        )

        self._populate_db()

    def _contour_to_embedding(self, contour: list[float], target_dim: int = 16) -> list[float]:
        """Convert pitch contour intervals into a fixed-length normalized vector embedding."""
        if not contour:
            vec = np.zeros(target_dim, dtype=np.float32)
        else:
            arr = np.array(contour, dtype=np.float32)
            # Resample or pad contour to fixed dimension
            if len(arr) != target_dim:
                x_old = np.linspace(0, 1, len(arr))
                x_new = np.linspace(0, 1, target_dim)
                vec = np.interp(x_new, x_old, arr)
            else:
                vec = arr

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def _populate_db(self):
        """Index pre-defined harmony knowledge base into ChromaDB."""
        if self.collection.count() > 0:
            return  # Already populated

        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for item in self.HARMONY_KNOWLEDGE_BASE:
            ids.append(item["id"])
            emb = self._contour_to_embedding(item["contour"])
            embeddings.append(emb)
            metadatas.append({
                "genre": item["genre"],
                "key_name": item["key_name"],
                "chord_names": ",".join(item["chord_names"]),
                "description": item["description"]
            })
            documents.append(f"{item['genre']} in {item['key_name']} ({item['description']})")

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def extract_melody_contour(self, notes: list[PitchNote]) -> list[float]:
        """Extract pitch interval contour from detected PitchNotes."""
        if not notes or len(notes) < 2:
            return [0.0]

        midi_pitches = [n.pitch_midi for n in notes]
        # Intervals relative to root note
        root = midi_pitches[0]
        intervals = [float(p - root) for p in midi_pitches]
        return intervals

    def retrieve_best_harmony(self, notes: list[PitchNote], top_k: int = 1) -> list[HarmonyMatch]:
        """Query Vector DB for matching chord harmonies based on hummed melody contour."""
        contour = self.extract_melody_contour(notes)
        query_embedding = self._contour_to_embedding(contour)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        matches: list[HarmonyMatch] = []
        if not results or not results["ids"] or len(results["ids"][0]) == 0:
            return matches

        for i in range(len(results["ids"][0])):
            item_id = results["ids"][0][i]
            dist = results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
            sim_score = max(0.0, 1.0 - float(dist))

            # Retrieve original item metadata
            meta = results["metadatas"][0][i]
            # Match item in knowledge base
            kb_item = next((item for item in self.HARMONY_KNOWLEDGE_BASE if item["id"] == item_id), None)
            if kb_item:
                matches.append(HarmonyMatch(
                    genre=kb_item["genre"],
                    key_name=kb_item["key_name"],
                    chord_names=kb_item["chord_names"],
                    chord_midis=kb_item["chord_midis"],
                    similarity_score=sim_score,
                    description=kb_item["description"]
                ))

        return matches

    def generate_backing_band(
        self, 
        harmony: HarmonyMatch, 
        duration_sec: float, 
        synth: MusicSynthesizer, 
        instrument: str = "Acoustic Guitar"
    ) -> np.ndarray:
        """Synthesize backing chord accompaniment audio for the retrieved harmony."""
        if not harmony.chord_midis or duration_sec <= 0:
            return np.zeros(int(duration_sec * synth.sr), dtype=np.float32)

        num_chords = len(harmony.chord_midis)
        chord_duration = duration_sec / float(num_chords)

        backing_notes: list[PitchNote] = []

        for idx, chord_triad in enumerate(harmony.chord_midis):
            st = idx * chord_duration
            et = st + chord_duration
            for midi_pitch in chord_triad:
                hz = PitchDetector.midi_to_hz(midi_pitch)
                name = PitchDetector.midi_to_note_name(midi_pitch)
                backing_notes.append(PitchNote(
                    pitch_midi=midi_pitch,
                    pitch_name=name,
                    frequency_hz=hz,
                    start_time=st,
                    end_time=et,
                    velocity=0.5  # Soft background volume
                ))

        backing_audio = synth.synthesize_tune(backing_notes, instrument=instrument)
        return backing_audio
