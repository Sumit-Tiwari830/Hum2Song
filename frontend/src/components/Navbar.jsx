import React from 'react';
import { Music, Sparkles, Cpu, Layers } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur-2xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
        
        {/* Brand & Logo */}
        <div className="flex items-center space-x-3.5">
          <div className="relative p-2.5 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-emerald-400 shadow-lg shadow-cyan-500/25">
            <Music className="w-6 h-6 text-slate-950 stroke-[2.5]" />
            <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-emerald-400 border-2 border-slate-950 animate-ping"></span>
          </div>
          <div>
            <div className="flex items-center space-x-2.5">
              <span className="font-extrabold text-xl text-white tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-300">
                Hum2Tune Studio
              </span>
              <span className="px-2.5 py-0.5 text-[10px] font-bold tracking-widest rounded-full bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 text-cyan-300 border border-cyan-500/30 uppercase">
                PRO FYP v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">Neural Pitch Extraction & Music Harmony RAG Engine</p>
          </div>
        </div>

        {/* Live Engine Badges */}
        <div className="hidden md:flex items-center space-x-3 text-xs font-semibold">
          <div className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-900/90 border border-white/10 text-slate-300 shadow-sm">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span>FastAPI & ChromaDB Vector DB</span>
          </div>

          <div className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-900/90 border border-white/10 text-slate-300 shadow-sm">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>Spotify Basic Pitch & pYIN</span>
          </div>

          <div className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span className="font-bold tracking-wider">ONLINE</span>
          </div>
        </div>

      </div>
    </header>
  );
}
