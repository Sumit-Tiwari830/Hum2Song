import React from 'react';
import { Activity, Music } from 'lucide-react';

export default function PianoRollVisualizer({ notes }) {
  if (!notes || notes.length === 0) return null;

  // Compute maximum end time for timeline scaling
  const maxTime = Math.max(...notes.map((n) => n.end_time)) || 4.0;
  const minMidi = Math.min(...notes.map((n) => n.pitch_midi)) - 2;
  const maxMidi = Math.max(...notes.map((n) => n.pitch_midi)) + 2;
  const midiRange = Math.max(1, maxMidi - minMidi);

  return (
    <div className="glass-card rounded-2xl p-6 border border-slate-800 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white flex items-center space-x-2">
          <Activity className="w-5 h-5 text-emerald-400" />
          <span>Interactive Piano Roll & Note Transcription</span>
        </h3>
        <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          {notes.length} Notes Detected
        </span>
      </div>

      {/* Piano Roll Grid Canvas / Visualizer */}
      <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 mb-5 relative overflow-hidden">
        <div className="h-44 relative flex flex-col justify-between">
          
          {/* Background Grid Lines */}
          <div className="absolute inset-0 grid grid-cols-8 divide-x divide-slate-800/40 pointer-events-none">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-full"></div>
            ))}
          </div>

          {/* Render Detected Note Blocks */}
          {notes.map((note, idx) => {
            const leftPct = (note.start_time / maxTime) * 100;
            const widthPct = Math.max(3, (note.duration / maxTime) * 100);
            const bottomPct = ((note.pitch_midi - minMidi) / midiRange) * 80 + 10;

            return (
              <div
                key={idx}
                style={{
                  left: `${leftPct}%`,
                  width: `${widthPct}%`,
                  bottom: `${bottomPct}%`,
                }}
                className="absolute h-6 rounded-md bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 font-bold text-[10px] flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-emerald-300/40 transition hover:scale-105"
                title={`${note.pitch_name} (MIDI ${note.pitch_midi}) - ${note.frequency_hz} Hz [${note.start_time}s - ${note.end_time}s]`}
              >
                {note.pitch_name}
              </div>
            );
          })}
        </div>

        {/* Timeline Axis Labels */}
        <div className="flex justify-between mt-2 pt-2 border-t border-slate-800 text-[10px] text-slate-500 font-mono">
          <span>0.0s</span>
          <span>{(maxTime * 0.25).toFixed(1)}s</span>
          <span>{(maxTime * 0.5).toFixed(1)}s</span>
          <span>{(maxTime * 0.75).toFixed(1)}s</span>
          <span>{maxTime.toFixed(1)}s</span>
        </div>
      </div>

      {/* Note List Badges Table */}
      <div className="flex flex-wrap gap-2">
        {notes.map((note, i) => (
          <div
            key={i}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono flex items-center space-x-2"
          >
            <Music className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-bold text-white">{note.pitch_name}</span>
            <span className="text-slate-500">|</span>
            <span className="text-slate-400">{note.frequency_hz} Hz</span>
            <span className="text-slate-500">|</span>
            <span className="text-slate-400">{note.duration}s</span>
          </div>
        ))}
      </div>
    </div>
  );
}
