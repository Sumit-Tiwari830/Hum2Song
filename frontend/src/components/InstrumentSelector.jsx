import React from 'react';
import { Sliders, Sparkles, Piano, Zap, Guitar, Wind, Disc, Gamepad2, ArrowRight } from 'lucide-react';

const INSTRUMENT_LIST = [
  { name: 'Grand Piano', desc: 'Acoustic Concert Grand', icon: Piano, color: 'from-amber-500/20 to-yellow-500/10 text-amber-400 border-amber-500/40 shadow-amber-500/10' },
  { name: 'Synth Lead', desc: 'Futuristic Sawtooth Lead', icon: Zap, color: 'from-cyan-500/20 to-blue-500/10 text-cyan-400 border-cyan-500/40 shadow-cyan-500/10' },
  { name: 'Acoustic Guitar', desc: 'Warm Nylon Plucked', icon: Guitar, color: 'from-orange-500/20 to-amber-500/10 text-orange-400 border-orange-500/40 shadow-orange-500/10' },
  { name: 'Flute', desc: 'Soft Woodwind Vibrato', icon: Wind, color: 'from-emerald-500/20 to-teal-500/10 text-emerald-400 border-emerald-500/40 shadow-emerald-500/10' },
  { name: 'Strings', desc: 'Orchestral Ensemble', icon: Disc, color: 'from-purple-500/20 to-indigo-500/10 text-purple-400 border-purple-500/40 shadow-purple-500/10' },
  { name: '8-Bit Chiptune', desc: 'Retro Arcade Square Wave', icon: Gamepad2, color: 'from-rose-500/20 to-pink-500/10 text-rose-400 border-rose-500/40 shadow-rose-500/10' },
];

export default function InstrumentSelector({
  selectedInstrument,
  onSelectInstrument,
  enableRagBacking,
  onToggleRag,
  onGenerate,
  isLoading,
  hasAudio
}) {
  return (
    <div className="glass-panel rounded-3xl p-6 md:p-7 border border-white/10 shadow-2xl">
      
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-inner">
            <Sliders className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-white">Synthesis & Instrument Controls</h3>
            <p className="text-xs text-slate-400">Select Instrument Timbre & Backing Modes</p>
          </div>
        </div>
      </div>

      {/* Instruments Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3.5 mb-6">
        {INSTRUMENT_LIST.map((inst) => {
          const IconComponent = inst.icon;
          const isSelected = selectedInstrument === inst.name;
          return (
            <button
              key={inst.name}
              onClick={() => onSelectInstrument(inst.name)}
              className={`p-4 rounded-2xl border text-left transition-all cursor-pointer relative overflow-hidden ${
                isSelected
                  ? `bg-gradient-to-br ${inst.color} border-2 shadow-lg scale-[1.02]`
                  : 'bg-slate-900/60 hover:bg-slate-800/80 border-white/5 text-slate-400 hover:text-slate-200'
              }`}
            >
              <IconComponent className={`w-6 h-6 mb-2 ${isSelected ? 'text-current' : 'text-slate-500'}`} />
              <p className="text-xs font-bold tracking-tight text-white">{inst.name}</p>
              <p className="text-[10px] text-slate-400 font-medium truncate mt-0.5">{inst.desc}</p>

              {isSelected && (
                <span className="absolute top-3 right-3 w-2 h-2 rounded-full bg-current"></span>
              )}
            </button>
          );
        })}
      </div>

      {/* Music Harmony RAG Toggle Card */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-slate-900/90 via-slate-900/80 to-indigo-950/40 border border-white/10 flex items-center justify-between mb-6 shadow-md">
        <div className="flex items-center space-x-3.5">
          <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white flex items-center space-x-2">
              <span>Music Harmony RAG Backing Band</span>
              <span className="px-2 py-0.5 text-[9px] font-extrabold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
                ChromaDB Vector DB
              </span>
            </h4>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Queries vector similarity database & generates matching backing chords
            </p>
          </div>
        </div>

        <button
          onClick={() => onToggleRag(!enableRagBacking)}
          className={`relative inline-flex h-7 w-12 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
            enableRagBacking ? 'bg-indigo-500' : 'bg-slate-800'
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow-md transition duration-200 ease-in-out ${
              enableRagBacking ? 'translate-x-5' : 'translate-x-0'
            }`}
          />
        </button>
      </div>

      {/* Primary Action Button */}
      <button
        onClick={onGenerate}
        disabled={!hasAudio || isLoading}
        className={`w-full py-4 rounded-2xl font-extrabold text-sm tracking-wide transition-all duration-300 flex items-center justify-center space-x-2.5 shadow-2xl ${
          !hasAudio
            ? 'bg-slate-900/80 border border-white/5 text-slate-600 cursor-not-allowed'
            : isLoading
            ? 'bg-indigo-600/60 text-indigo-100 cursor-wait shadow-indigo-500/20 animate-pulse'
            : 'bg-gradient-to-r from-cyan-500 via-indigo-500 to-emerald-400 hover:from-cyan-400 hover:via-indigo-400 hover:to-emerald-300 text-slate-950 shadow-cyan-500/30 cursor-pointer transform hover:scale-[1.01]'
        }`}
      >
        {isLoading ? (
          <>
            <span className="w-5 h-5 rounded-full border-3 border-slate-950 border-t-transparent animate-spin"></span>
            <span>Synthesizing Music & Querying Vector RAG...</span>
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5 stroke-[2.5]" />
            <span>Generate Instrument Tune & Backing Band</span>
            <ArrowRight className="w-4 h-4" />
          </>
        )}
      </button>
    </div>
  );
}
