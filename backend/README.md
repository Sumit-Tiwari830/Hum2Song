# 🎵 Hum2Tune: AI-Powered Humming-to-Music Synthesizer & Music RAG Engine

> **Final Year Project (FYP)**  
> **Author**: Kiran Tiwari  
> **Environment**: WSL / Ubuntu (`kirantiwari@kirantiwari:~/FYP-1`) & Windows 11  

---

## 🌟 Overview & FYP Highlights

**Hum2Tune** is a prize-winning AI Final Year Project that converts raw human humming recordings into multi-instrument musical tracks (Grand Piano, Synth Lead, Acoustic Guitar, Flute, Strings, 8-Bit Chiptune) and downloadable standard `.mid` MIDI files.

### 🏆 Key Novelty & Prize-Winning Features:
1. **Signal Processing & Audio Engineering (DSP)**: Noise gating, peak amplitude normalization, and sample rate normalization (22.05 kHz).
2. **Pitch Detection**: Probabilistic YIN (pYIN) pitch estimation for note segmentation, frequency extraction, and onset/offset timing.
3. **Music Harmony RAG (Retrieval-Augmented Generation)**: Vector search (ChromaDB) indexing musical theory progressions (Pop, Jazz, Rock, Lofi, Cinematic Epic). Queries vector embeddings of the hummed melody to automatically generate a full **polyphonic backing band** behind the lead line!
4. **Multi-Instrument Audio Synthesizer**: Custom waveform synthesis engine with ADSR (Attack-Decay-Sustain-Release) amplitude envelopes.
5. **FastAPI REST Backend**: Production-ready API ready to connect with React.js frontend applications.

---

## 🏗️ System Architecture

```
[🎤 Raw Humming Audio]
          │
          ▼
 [🧹 Audio Preprocessor]  ➔  Noise Gate (-40 dBFS) & Peak Normalization (-3 dBFS)
          │
          ▼
  [🎵 Pitch Detector]    ➔  pYIN Frequency Tracking & Note Event Segmentation
          │
          ├─────────────────────────────────────────┐
          ▼                                         ▼
[🎹 Multi-Instrument Synth]               [🔍 Music Harmony RAG Engine]
(Piano, Synth, Guitar, Flute...)          (ChromaDB Cosine Vector Search)
          │                                         │
          └────────────────────┬────────────────────┘
                               ▼
                   [🎛️ Audio & Backing Mixer]
                               │
                               ▼
               [🚀 FastAPI Backend REST Server]
              (Exports .wav Audio & .mid MIDI)
```

---

## 💻 Directory Structure

```
~/FYP-1/fyp_humming_to_tune/
├── main.py                     # FastAPI REST server & API endpoints
├── requirements.txt           # Pinned dependency requirements
├── README.md                  # Complete documentation & usage guide
├── src/
│   ├── __init__.py
│   ├── audio_processor.py     # Preprocessing (filtering, normalization, noise gate)
│   ├── pitch_detector.py      # Pitch extraction & note event segmentation
│   ├── synthesizer.py         # Multi-instrument audio synth & MIDI exporter
│   └── harmony_rag.py         # ChromaDB Vector DB & Music Harmony RAG engine
├── tests/                     # Comprehensive test suite (14 Unit Tests)
│   ├── test_audio_processor.py
│   ├── test_pitch_detector.py
│   ├── test_synthesizer.py
│   ├── test_harmony_rag.py
│   └── test_api.py
└── output/                    # Generated WAV and MIDI files
```

---

## 🚀 Step-by-Step Setup & Execution Guide (WSL)

### 1. Navigate to Project & Activate Virtual Environment
Open your WSL terminal (`kirantiwari@kirantiwari:~/FYP-1`):

```bash
cd ~/FYP-1
source venv/bin/activate
cd fyp_humming_to_tune
```

### 2. Run Automated Test Suite
Verify that all 14 unit tests pass cleanly:

```bash
python -m unittest discover tests
```

Expected Output:
```
..............
Ran 14 tests in ~3.5s
OK
```

### 3. Launch FastAPI Server
Run the backend server on port 8000:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open your web browser and visit:
* **Interactive API Documentation (Swagger UI)**: `http://localhost:8000/docs`
* **Health Check**: `http://localhost:8000/health`

---

## 🌐 REST API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server health check. |
| `GET` | `/api/instruments` | Get list of available synth instruments. |
| `POST` | `/api/process-humming` | Upload humming audio file, extract notes, retrieve RAG backing chords, synthesize audio tune, and return MIDI + WAV download URLs. |
| `GET` | `/api/download/{filename}` | Download generated `.wav` audio track or `.mid` MIDI file. |

---

## 🎓 Thesis & FYP Presentation Tips

1. **Theoretical Deep-Dive**: Present the mathematical formulation of STFT, pYIN autocorrelation, ADSR amplitude envelope math, and Cosine similarity for Vector RAG retrieval.
2. **Empirical Benchmarks**: Showcase the test execution logs and note extraction latency (~0.08s per audio segment).
3. **MIDI Compatibility**: Demonstrate importing the output `.mid` file into DAWs like FL Studio, Ableton Live, or GarageBand.
