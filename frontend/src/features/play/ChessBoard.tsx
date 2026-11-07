import React, { useEffect, useMemo, useState } from 'react';
import { Chess } from 'chess.js';
import { ChessPiece } from './ChessPiece';

interface ChessBoardProps {
  fen: string;
  orientation: 'white' | 'black';
  disabled?: boolean;
  lastMove?: string;
  onMove: (uci: string) => void;
}

export const ChessBoard: React.FC<ChessBoardProps> = ({
  fen,
  orientation,
  disabled = false,
  lastMove,
  onMove,
}) => {
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const chess = useMemo(() => new Chess(fen), [fen]);

  useEffect(() => setSelectedSquare(null), [fen]);

  const ranks = orientation === 'white' ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];
  const files = orientation === 'white' ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0];

  const handleSquareClick = (square: string) => {
    if (disabled) return;
    const piece = chess.get(square as never);

    if (!selectedSquare) {
      if (piece?.color === chess.turn()) setSelectedSquare(square);
      return;
    }

    if (selectedSquare === square) {
      setSelectedSquare(null);
      return;
    }

    try {
      const move = chess.move({ from: selectedSquare, to: square, promotion: 'q' });
      setSelectedSquare(null);
      onMove(move.lan);
    } catch {
      if (piece?.color === chess.turn()) setSelectedSquare(square);
      else setSelectedSquare(null);
    }
  };

  return (
    <div className="board-frame">
      <div className="chess-board" role="grid" aria-label="Interactive chess board">
        {ranks.map((rank) =>
          files.map((file) => {
            const square = `${String.fromCharCode(97 + file)}${rank + 1}`;
            const boardPiece = chess.board()[7 - rank][file];
            const selected = selectedSquare === square;
            const inLastMove = lastMove?.slice(0, 2) === square || lastMove?.slice(2, 4) === square;
            const light = (rank + file) % 2 !== 0;
            const showRank = file === (orientation === 'white' ? 0 : 7);
            const showFile = rank === (orientation === 'white' ? 0 : 7);

            return (
              <button
                type="button"
                role="gridcell"
                key={square}
                aria-label={`${square}${boardPiece ? ` ${boardPiece.color === 'w' ? 'white' : 'black'} ${boardPiece.type}` : ''}`}
                onClick={() => handleSquareClick(square)}
                className={`board-square ${light ? 'board-square-light' : 'board-square-dark'} ${selected ? 'board-square-selected' : ''} ${inLastMove ? 'board-square-last' : ''}`}
              >
                {showRank && <span className="board-coordinate board-rank">{rank + 1}</span>}
                {showFile && <span className="board-coordinate board-file">{String.fromCharCode(97 + file)}</span>}
                {boardPiece && <ChessPiece color={boardPiece.color} type={boardPiece.type} />}
              </button>
            );
          }),
        )}
      </div>
    </div>
  );
};
