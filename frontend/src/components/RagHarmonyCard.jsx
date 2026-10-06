import React from 'react';
import { Sparkles, Database, Music2, ShieldCheck } from 'lucide-react';

export default function RagHarmonyCard({ ragData }) {
  if (!ragData || !ragData.genre || ragData.genre === 'N/A') return null;

  const matchPct = Math.round((ragData.similarity_score || 0.85) * 100);

  return (
    <div className="glass-card rounded-2xl p-6 border border-slate-800 shadow-xl bg-gradient-to-br from-slate-900/90 via-indigo-950/20 to-slate-900/90">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white flex items-center space-x-2">
          <Database className="w-5 h-5 text-indigo-400" />
          <span>Vector RAG Harmony Recommendation</span>
        </h3>
        <span className="px-3 py-1 text-xs font-bold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
          <span>{matchPct}% Vector Match</span>
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Genre Style */}
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Genre Style</p>
          <p className="text-sm font-bold text-cyan-400 flex items-center space-x-1.5">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>{ragData.genre}</span>
          </p>
        </div>

        {/* Key Signature */}
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Key Signature</p>
          <p className="text-sm font-bold text-emerald-400 flex items-center space-x-1.5">
            <Music2 className="w-4 h-4 text-emerald-400" />
            <span>{ragData.key_name}</span>
          </p>
        </div>

        {/* Backing Chords Sequence */}
        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Backing Chords</p>
          <div className="flex items-center space-x-1.5 font-mono text-xs font-bold text-amber-400">
            {ragData.chord_names?.map((chord, idx) => (
              <React.Fragment key={idx}>
                <span className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">{chord}</span>
                {idx < ragData.chord_names.length - 1 && <span className="text-slate-600">→</span>}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      <p className="text-xs text-slate-400 italic bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
        💡 <span className="font-semibold text-slate-300">RAG Musicology Insight:</span> {ragData.description}
      </p>
    </div>
  );
}
