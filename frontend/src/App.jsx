import React, { useState } from 'react';
import Navbar from './components/Navbar';
import AudioRecorder from './components/AudioRecorder';
import InstrumentSelector from './components/InstrumentSelector';
import PianoRollVisualizer from './components/PianoRollVisualizer';
import RagHarmonyCard from './components/RagHarmonyCard';
import AudioOutputCard from './components/AudioOutputCard';

export default function App() {
  const [audioFile, setAudioFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [selectedInstrument, setSelectedInstrument] = useState('Grand Piano');
  const [enableRagBacking, setEnableRagBacking] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Result States from Backend REST API
  const [resultData, setResultData] = useState(null);

  const handleAudioReady = (file, url) => {
    setAudioFile(file);
    setAudioUrl(url);
    setResultData(null);
    setErrorMsg(null);
  };

  const handleGenerateTune = async () => {
    if (!audioFile) {
      setErrorMsg('Please record or upload a humming audio file first.');
      return;
    }

    setIsLoading(true);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('file', audioFile);
    formData.append('instrument', selectedInstrument);
    formData.append('enable_rag_backing', enableRagBacking ? 'true' : 'false');

    try {
      const response = await fetch('/api/process-humming', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process humming audio.');
      }

      const data = await response.json();
      setResultData(data);
    } catch (err) {
      setErrorMsg(err.message || 'Error connecting to backend API.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <Navbar />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Hero Welcome Banner */}
        <div className="text-center max-w-3xl mx-auto space-y-2">
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Humming to <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-indigo-400 to-emerald-400">Multi-Instrument Music</span>
          </h1>
          <p className="text-sm text-slate-400">
            Convert your voice into studio instrumental tracks and retrieve matching chord harmonies with Vector RAG
          </p>
        </div>

        {/* Error Alert Message */}
        {errorMsg && (
          <div className="max-w-3xl mx-auto p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-medium flex items-center justify-between">
            <span>⚠️ {errorMsg}</span>
            <button onClick={() => setErrorMsg(null)} className="text-rose-400 hover:text-white font-bold">×</button>
          </div>
        )}

        {/* Core Input & Control Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AudioRecorder onAudioReady={handleAudioReady} audioFile={audioFile} />
          
          <InstrumentSelector
            selectedInstrument={selectedInstrument}
            onSelectInstrument={setSelectedInstrument}
            enableRagBacking={enableRagBacking}
            onToggleRag={setEnableRagBacking}
            onGenerate={handleGenerateTune}
            isLoading={isLoading}
            hasAudio={!!audioFile}
          />
        </div>

        {/* Output & Visualizers Section */}
        {resultData && (
          <div className="space-y-6 animate-fade-in">
            <AudioOutputCard
              audioUrl={resultData.synthesized_audio_url}
              midiUrl={resultData.midi_file_url}
              originalAudioUrl={audioUrl}
              instrument={selectedInstrument}
            />

            <RagHarmonyCard ragData={resultData.rag_harmony} />

            <PianoRollVisualizer notes={resultData.notes} />
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        <p>Hum2Tune Final Year Project © 2026 | Built with Python, Spotify Basic Pitch, ChromaDB RAG, FastAPI & React</p>
      </footer>
    </div>
  );
}
