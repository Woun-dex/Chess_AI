import React from 'react';

interface ChessPieceProps {
  color: 'w' | 'b';
  type: 'p' | 'n' | 'b' | 'r' | 'q' | 'k';
}

// Piece artwork: Cburnett, Wikimedia Commons, CC BY-SA 3.0.
// The original SVG files are kept locally in public/pieces for offline rendering.
export const ChessPiece: React.FC<ChessPieceProps> = ({ color, type }) => (
  <img
    className="chess-piece"
    src={`/pieces/chess-${type}${color === 'w' ? 'lt' : 'dt'}45.svg`}
    alt=""
    draggable={false}
  />
);
