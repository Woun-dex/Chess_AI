import React, { useEffect, useRef } from 'react';
import { ArrowRight, Crown, RotateCcw, Sparkles, X } from 'lucide-react';
import { Color, GameResponse } from '../../types/chess';

interface CheckmateModalProps {
  game: GameResponse;
  playerColor: Color;
  onClose: () => void;
  onNewGame: () => void;
  onReview: () => void;
}

export const CheckmateModal: React.FC<CheckmateModalProps> = ({
  game,
  playerColor,
  onClose,
  onNewGame,
  onReview,
}) => {
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const playerWon = game.winner === playerColor;

  useEffect(() => {
    closeButtonRef.current?.focus();
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div
      className="result-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        className="result-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="checkmate-title"
        aria-describedby="checkmate-description"
      >
        <button
          ref={closeButtonRef}
          type="button"
          className="result-close"
          onClick={onClose}
          aria-label="Close game result"
        >
          <X size={17} />
        </button>

        <div className={`result-emblem ${playerWon ? 'result-emblem-win' : 'result-emblem-loss'}`}>
          <div className="result-emblem-ring">
            {playerWon ? <Crown size={30} strokeWidth={1.6} /> : <Sparkles size={28} strokeWidth={1.6} />}
          </div>
        </div>

        <p className="eyebrow result-eyebrow">GAME COMPLETE · CHECKMATE</p>
        <h2 id="checkmate-title">{playerWon ? 'A beautiful finish.' : 'The king is cornered.'}</h2>
        <p id="checkmate-description" className="result-description">
          {playerWon
            ? 'Your calculation held up under pressure. Take a moment to see what made this win yours.'
            : 'Your opponent found the decisive line. Every checkmate is a lesson waiting to be replayed.'}
        </p>

        <div className="result-score">
          <span>{playerWon ? 'VICTORY' : 'GAME OVER'}</span>
          <strong>{game.moves.length} <small>moves</small></strong>
        </div>

        <div className="result-actions">
          <button type="button" className="result-primary" onClick={onReview}>
            Review the game <ArrowRight size={16} />
          </button>
          <button type="button" className="result-secondary" onClick={onNewGame}>
            <RotateCcw size={15} /> Play again
          </button>
        </div>
        <button type="button" className="result-text-button" onClick={onClose}>
          Stay on the board
        </button>
      </section>
    </div>
  );
};
