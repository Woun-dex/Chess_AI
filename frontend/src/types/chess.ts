export type Color = 'white' | 'black';

export type GameStatus =
  | 'in_progress'
  | 'checkmate'
  | 'stalemate'
  | 'insufficient_material'
  | 'seventyfive_moves'
  | 'fivefold_repetition'
  | 'resigned'
  | 'draw_agreed';

export type MoveClassification =
  | 'brilliant'
  | 'great'
  | 'best'
  | 'excellent'
  | 'good'
  | 'inaccuracy'
  | 'mistake'
  | 'blunder';

export interface MoveRecord {
  move_id: string;
  uci: string;
  san: string;
  fen_before: string;
  fen_after: string;
  move_number: number;
  color: Color;
  classification?: MoveClassification;
}

export interface PositionEvaluation {
  fen: string;
  centipawns: number | null;
  mate_in: number | null;
  best_move_uci: string;
  pv: string[];
  depth: number;
}

export interface TutorMessage {
  id: string;
  sender: 'tutor' | 'student';
  content: string;
  timestamp: string;
  fenContext?: string;
}
