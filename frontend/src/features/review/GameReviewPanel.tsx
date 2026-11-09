import React from 'react';
import { Sparkles } from 'lucide-react';
import { GameReview } from '../../types/chess';

interface GameReviewPanelProps {
  review: GameReview;
}

export const GameReviewPanel: React.FC<GameReviewPanelProps> = ({ review }) => (
  <div className="panel review-panel">
    <div className="panel-title">
      <span><Sparkles size={16} /> GAME REVIEW</span>
      <span className="move-count">depth {review.depth} · MultiPV {review.multipv}</span>
    </div>
    <p className="review-summary">{review.summary}</p>
    <div className="coach-callout">
      <Sparkles size={15} />
      <div><strong>Coach's perspective</strong><span>{review.moves.find((move) => move.classification === 'blunder' || move.classification === 'mistake') ? 'Focus on the critical moments below. Compare your move with the engine variation, then replay the position.' : 'Your decision-making was consistent. Replay the alternative lines to turn good moves into reliable habits.'}</span></div>
    </div>
    <div className="accuracy-grid">
      <span>White <strong>{review.accuracy.white}%</strong></span>
      <span>Black <strong>{review.accuracy.black}%</strong></span>
    </div>
    <div className="review-counts">
      {Object.entries(review.classification_counts).map(([classification, count]) => (
        <span key={classification}><strong>{count}</strong> {classification}</span>
      ))}
    </div>
    <div className="review-moves">
      {review.moves.map((move) => (
        <div className={`review-move review-${move.classification}`} key={`${move.move_number}-${move.move_uci}`}>
          <span>{move.move_number}. {move.move_san}</span>
          <strong>{move.classification}</strong>
          <small>{move.centipawn_loss} CPL{move.tactical_motifs.length ? ` · ${move.tactical_motifs.join(', ')}` : ''}</small>
          <p><span className="coach-label">Tutor explanation</span>{move.coach_explanation}</p>
          <em>{move.classification === 'blunder' || move.classification === 'mistake' ? `Try ${move.score_before.best_move_uci || 'the engine line'} instead` : move.score_after.pv.slice(0, 3).join(' ')}</em>
        </div>
      ))}
    </div>
  </div>
);
