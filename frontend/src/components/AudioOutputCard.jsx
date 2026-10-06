import React from 'react';
import { Volume2, Download, Music, Play, Disc } from 'lucide-react';

export default function AudioOutputCard({ audioUrl, midiUrl, originalAudioUrl, instrument }) {
  if (!audioUrl) return null;

  return (
    <div className="glass-card rounded-2xl p-6 border border-slate-800 shadow-xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-cyan-950/20">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white flex items-center space-x-2">
          <Volume2 className="w-5 h-5 text-cyan-400" />
          <span>Synthesized Music & Downloads</span>
        </h3>
        <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center space-x-1.5">
          <Disc className="w-3.5 h-3.5 animate-spin" />
          <span>{instrument || 'Grand Piano'}</span>
        </span>
      </div>

      {/* Animated Equalizer Wave Animation */}
      <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 mb-5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Music className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm font-bold text-white">Synthesized Audio Track</p>
            <p className="text-xs text-slate-400">High-fidelity 22.05 kHz Output + ADSR Envelopes</p>
          </div>
        </div>

        {/* Equalizer Bars */}
        <div className="flex items-end space-x-1 h-7">
          <div className="w-1.5 bg-cyan-400 rounded-full animate-eq-1"></div>
          <div className="w-1.5 bg-emerald-400 rounded-full animate-eq-2"></div>
          <div className="w-1.5 bg-indigo-400 rounded-full animate-eq-3"></div>
          <div className="w-1.5 bg-cyan-400 rounded-full animate-eq-4"></div>
          <div className="w-1.5 bg-emerald-400 rounded-full animate-eq-1"></div>
        </div>
      </div>

      {/* Dual Audio Player Controls */}
      <div className="space-y-3 mb-5">
        {/* Synthesized Tune Audio Player */}
        <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
          <label className="block text-xs font-semibold text-slate-300 mb-2">🎹 Synthesized Instrument Tune</label>
          <audio controls src={audioUrl} className="w-full h-10 rounded-lg bg-slate-950" />
        </div>

        {/* Original Humming Audio Player */}
        {originalAudioUrl && (
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <label className="block text-xs font-medium text-slate-400 mb-2">🎤 Original Raw Humming Recording</label>
            <audio controls src={originalAudioUrl} className="w-full h-10 rounded-lg bg-slate-950" />
          </div>
        )}
      </div>

      {/* Download Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <a
          href={audioUrl}
          download="synthesized_tune.wav"
          className="flex items-center justify-center space-x-2 px-4 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold transition shadow-lg shadow-cyan-500/20"
        >
          <Download className="w-5 h-5" />
          <span>Download Audio (.wav)</span>
        </a>

        <a
          href={midiUrl}
          download="synthesized_tune.mid"
          className="flex items-center justify-center space-x-2 px-4 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition shadow-lg shadow-indigo-600/30"
        >
          <Music className="w-5 h-5" />
          <span>Download MIDI Track (.mid)</span>
        </a>
      </div>
    </div>
  );
}
