import React from 'react';
import { Sparkles, BookOpen, Trophy } from 'lucide-react';

interface HeaderProps {
  status: string;
}

export const Header: React.FC<HeaderProps> = ({ status }) => {
  return (
    <header className="w-full bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between shadow-md">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-xl text-white shadow">
          ♟
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            Grandmaster AI <span className="text-xs bg-indigo-900/60 text-indigo-300 font-medium px-2 py-0.5 rounded border border-indigo-700">Tutor</span>
          </h1>
          <p className="text-xs text-slate-400">Stockfish 16 Engine + Pedagogical LLM Coach</p>
        </div>
      </div>

      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2 text-sm text-slate-300">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Backend: <strong className="text-emerald-400 uppercase">{status}</strong></span>
        </div>

        <nav className="flex space-x-2">
          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium bg-slate-700 hover:bg-slate-600 text-slate-200 transition">
            <Trophy className="w-4 h-4 text-amber-400" /> Play
          </button>
          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium bg-slate-700 hover:bg-slate-600 text-slate-200 transition">
            <Sparkles className="w-4 h-4 text-cyan-400" /> Review
          </button>
          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium bg-slate-700 hover:bg-slate-600 text-slate-200 transition">
            <BookOpen className="w-4 h-4 text-indigo-400" /> Curriculum
          </button>
        </nav>
      </div>
    </header>
  );
};
