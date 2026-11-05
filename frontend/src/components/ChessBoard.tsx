import React, { useState } from 'react';
import { Chess } from 'chess.js';

interface ChessBoardProps {
  fen: string;
  onMove?: (uci: string, san: string) => void;
  orientation?: 'white' | 'black';
}

const PIECE_UNICODE: Record<string, string> = {
  p: '♟', r: '♜', n: '♞', b: '♝', q: '♛', k: '♚',
  P: '♙', R: '♖', N: '♘', B: '♗', Q: '♕', K: '♔'
};

export const ChessBoard: React.FC<ChessBoardProps> = ({
  fen,
  onMove,
  orientation = 'white'
}) => {
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);

  const chess = new Chess(fen);
  const board = chess.board();

  const handleSquareClick = (squareName: string) => {
    if (!selectedSquare) {
      // Pick piece if it belongs to current player's turn
      const piece = chess.get(squareName as any);
      if (piece && piece.color === chess.turn()) {
        setSelectedSquare(squareName);
      }
      return;
    }

    if (selectedSquare === squareName) {
      setSelectedSquare(null);
      return;
    }

    // Try making a move
    try {
      const move = chess.move({
        from: selectedSquare,
        to: squareName,
        promotion: 'q',
      });

      if (move && onMove) {
        onMove(move.lan, move.san);
      }
      setSelectedSquare(null);
    } catch {
      // If clicked another piece of same color, reselect
      const piece = chess.get(squareName as any);
      if (piece && piece.color === chess.turn()) {
        setSelectedSquare(squareName);
      } else {
        setSelectedSquare(null);
      }
    }
  };

  const ranks = orientation === 'white' ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];
  const files = orientation === 'white' ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0];

  return (
    <div className="relative p-2 bg-slate-800 rounded-xl shadow-2xl border border-slate-700">
      <div className="grid grid-cols-8 grid-rows-8 w-[480px] h-[480px] border border-slate-600 rounded-lg overflow-hidden select-none">
        {ranks.map((rankIdx) =>
          files.map((fileIdx) => {
            const squareName = `${String.fromCharCode(97 + fileIdx)}${rankIdx + 1}`;
            const isLight = (rankIdx + fileIdx) % 2 !== 0;
            const piece = board[7 - rankIdx][fileIdx];
            const isSelected = selectedSquare === squareName;

            let bgColor = isLight ? 'bg-[#eeeed2]' : 'bg-[#769656]';
            if (isSelected) {
              bgColor = 'bg-amber-300 ring-2 ring-amber-500 ring-inset';
            }

            return (
              <div
                key={squareName}
                onClick={() => handleSquareClick(squareName)}
                className={`relative flex items-center justify-center cursor-pointer ${bgColor} transition-colors duration-150`}
              >
                {/* Board coordinates indicator */}
                {fileIdx === (orientation === 'white' ? 0 : 7) && (
                  <span className={`absolute top-0.5 left-1 text-[10px] font-bold ${isLight ? 'text-[#769656]' : 'text-[#eeeed2]'}`}>
                    {rankIdx + 1}
                  </span>
                )}
                {rankIdx === (orientation === 'white' ? 0 : 7) && (
                  <span className={`absolute bottom-0.5 right-1 text-[10px] font-bold ${isLight ? 'text-[#769656]' : 'text-[#eeeed2]'}`}>
                    {String.fromCharCode(97 + fileIdx)}
                  </span>
                )}

                {/* Piece glyph */}
                {piece && (
                  <span
                    className={`text-4xl drop-shadow-sm transition-transform active:scale-95 ${
                      piece.color === 'w' ? 'text-white drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]' : 'text-slate-900'
                    }`}
                  >
                    {PIECE_UNICODE[piece.color === 'w' ? piece.type.toUpperCase() : piece.type]}
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

