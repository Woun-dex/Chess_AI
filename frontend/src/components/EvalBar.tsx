import React from 'react';

interface EvalBarProps {
  centipawns: number | null;
  mateIn: number | null;
}

export const EvalBar: React.FC<EvalBarProps> = ({ centipawns, mateIn }) => {
  // Compute percentage (50% = equal 0.00, 100% = white winning, 0% = black winning)
  let whitePercent = 50;
  let evalText = '0.0';

  if (mateIn !== null) {
    evalText = `M${Math.abs(mateIn)}`;
    whitePercent = mateIn > 0 ? 100 : 0;
  } else if (centipawns !== null) {
    const pawns = centipawns / 100;
    evalText = pawns > 0 ? `+${pawns.toFixed(1)}` : pawns.toFixed(1);
    // Sigmoid scaling so large scores don't break UI: 1 / (1 + 10^(-score/4))
    const winProb = 1 / (1 + Math.pow(10, -pawns / 4));
    whitePercent = Math.min(Math.max(winProb * 100, 5), 95);
  }

  return (
    <div className="flex flex-col items-center h-[480px] w-8 bg-slate-950 rounded-lg overflow-hidden border border-slate-700 shadow-inner relative">
      {/* Black evaluation background */}
      <div className="w-full bg-slate-900 transition-all duration-300" style={{ height: `${100 - whitePercent}%` }} />
      {/* White evaluation background */}
      <div className="w-full bg-slate-100 transition-all duration-300" style={{ height: `${whitePercent}%` }} />
      
      {/* Absolute evaluation label */}
      <span className="absolute bottom-2 text-[10px] font-mono font-bold px-1 rounded bg-black/60 text-white">
        {evalText}
      </span>
    </div>
  );
};

