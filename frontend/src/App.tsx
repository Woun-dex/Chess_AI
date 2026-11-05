import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { ChessBoard } from './components/ChessBoard';
import { EvalBar } from './components/EvalBar';
import { TutorCoach } from './components/TutorCoach';
import { checkBackendHealth } from './services/api';
import { MoveRecord } from './types/chess';
import { RotateCcw, ShieldAlert } from 'lucide-react';

export const App: React.FC = () => {
  const [fen, setFen] = useState('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');
  const [moves, setMoves] = useState<MoveRecord[]>([]);
  const [backendStatus, setBackendStatus] = useState<string>('connecting...');
  const [evalScore, setEvalScore] = useState<number | null>(20); // +0.20 opening edge
  const [mateIn, setMateIn] = useState<number | null>(null);

  useEffect(() => {
    checkBackendHealth()
      .then((res) => setBackendStatus(res.status))
      .catch(() => setBackendStatus('mock-mode'));
  }, []);

  const handleMove = (uci: string, san: string) => {
    // Record move
    const newMove: MoveRecord = {
      move_id: String(Date.now()),
      uci,
      san,
      fen_before: fen,
      fen_after: fen, // Will be updated on actual chess state sync
      move_number: moves.length + 1,
      color: moves.length % 2 === 0 ? 'white' : 'black',
    };
    setMoves((prev) => [...prev, newMove]);
  };

  const resetBoard = () => {
    setFen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');
    setMoves([]);
    setEvalScore(20);
    setMateIn(null);
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-900 text-slate-100">
      <Header status={backendStatus} />

      <main className="flex-1 max-w-7xl mx-auto w-full p-6 flex flex-col gap-6">
        {/* Banner highlighting the core engineering decision */}
        <div className="bg-gradient-to-r from-indigo-950/80 via-slate-800 to-slate-900 border border-indigo-700/40 rounded-xl p-4 flex items-center justify-between shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-500/20 text-indigo-300 rounded-lg">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">
                Core Architectural Rule Enforced
              </h2>
              <p className="text-xs text-slate-300">
                Stockfish is the single authority for calculations & evaluations; LLM is responsible solely for teaching & explanations.
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={resetBoard}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-700 hover:bg-slate-600 text-slate-200 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Reset Game
            </button>
          </div>
        </div>

        {/* Interactive Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Evaluation Bar + Chessboard */}
          <div className="lg:col-span-8 flex flex-col md:flex-row items-center justify-center gap-4 bg-slate-850 p-6 rounded-2xl border border-slate-750 shadow-xl">
            <EvalBar centipawns={evalScore} mateIn={mateIn} />
            <div className="flex flex-col items-center gap-4">
              <ChessBoard fen={fen} onMove={handleMove} />
              
              {/* Move history list strip */}
              <div className="w-full max-w-[480px] bg-slate-800/80 rounded-lg p-2.5 border border-slate-700/60 flex items-center gap-2 overflow-x-auto text-xs font-mono">
                <span className="text-slate-400 font-sans font-medium">Moves:</span>
                {moves.length === 0 && <span className="text-slate-500 italic">No moves yet</span>}
                {moves.map((m, idx) => (
                  <span
                    key={m.move_id}
                    className="px-2 py-0.5 rounded bg-slate-700 text-slate-200 border border-slate-600"
                  >
                    {idx % 2 === 0 ? `${Math.floor(idx / 2) + 1}. ` : ''}{m.san}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: AI Tutor Chat */}
          <div className="lg:col-span-4 flex justify-center">
            <TutorCoach
              currentFen={fen}
              lastMoveSan={moves[moves.length - 1]?.san}
              centipawns={evalScore}
            />
          </div>
        </div>
      </main>
    </div>
  );
};
