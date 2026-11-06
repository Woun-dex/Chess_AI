import React from 'react';

interface ChessPieceProps {
  color: 'w' | 'b';
  type: 'p' | 'n' | 'b' | 'r' | 'q' | 'k';
}

const paths: Record<ChessPieceProps['type'], string> = {
  p: 'M12 3.5a3.5 3.5 0 1 1 0 7 3.5 3.5 0 0 1 0-7ZM8.1 11.1c.7 1.4 1.2 2.4 1.2 4.1l-3.1 2.6v1.7h11.6v-1.7l-3.1-2.6c0-1.7.5-2.7 1.2-4.1A5.2 5.2 0 0 0 12 10a5.2 5.2 0 0 0-3.9 1.1Z',
  r: 'M6 4h3v3h2V4h2v3h2V4h3l-1 5.2v7.1l1.5 1.7v1H5.5v-1L7 16.3V9.2L6 4Z',
  n: 'M7 19h11v-1.7l-2.3-1.5c.6-2.7.2-5.3-1.2-7.5l-2.4-3.6-2.5 1.5 1.1 2.7c-2.3.8-4 2.7-4.4 5.2L5 17.3V19h2Zm2-3.2c.7-2 2.1-3.3 4.2-3.7l.5-.1.4-.7c.5 1.4.5 2.8 0 4.3l-.2.5 1.7 1.2H8l1-1.5Z',
  b: 'M12 3.2c-2.1 1.5-3.2 3.3-3.2 5.2 0 1.8 1.2 3.1 2.2 4.1l-1.1 1.2-3.3 3.4v2h10.8v-2l-3.3-3.4-1.1-1.2c1-1 2.2-2.3 2.2-4.1 0-1.9-1.1-3.7-3.2-5.2Z',
  q: 'M5 5.2 7.5 7 9 4.2l3 3.1 3-3.1L16.5 7 19 5.2l-1.4 8.5H6.4L5 5.2Zm1.2 10h11.6l.8 2.3H5.4l.8-2.3Z',
  k: 'M10.8 3h2.4v2.3h2.3v2.4h-2.3v2.1c1.7.8 2.8 2.5 2.8 4.4v1.1l1.5 1.4v1H6.5v-1L8 15.3v-1.1c0-1.9 1.1-3.6 2.8-4.4V7.7H8.5V5.3h2.3V3Z',
};

export const ChessPiece: React.FC<ChessPieceProps> = ({ color, type }) => (
  <svg className={`chess-piece ${color === 'w' ? 'chess-piece-white' : 'chess-piece-black'}`} viewBox="0 0 24 24" aria-hidden="true">
    <path d={paths[type]} />
  </svg>
);
