export type Color = 'white' | 'black';

export type GameStatus =
  | 'in_progress'
  | 'checkmate'
  | 'stalemate'
  | 'insufficient_material'
  | 'seventyfive_moves'
  | 'fivefold_repetition'
  | 'resigned'
  | 'draw_agreed'
  | 'timeout';

export type OpponentType = 'stockfish' | 'random' | 'human';

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

export interface GameResponse {
  game_id: string;
  status: GameStatus;
  turn: Color;
  fen: string;
  version: number;
  white_player_id: string;
  black_player_id: string;
  opponent_type: OpponentType;
  bot_skill_level: number;
  time_control_seconds: number | null;
  winner: Color | 'draw' | null;
  moves: {
    move_id: string;
    uci: string;
    san: string;
    fen_after: string;
    color: Color;
  }[];
}

export interface CreateGamePayload {
  white_player_id: string;
  black_player_id: string;
  opponent_type: OpponentType;
  bot_skill_level: number;
  time_control_seconds: number | null;
}

export interface MakeMovePayload {
  move: string;
  player_id: string;
  expected_version: number;
}

export interface GameSettings {
  playerColor: 'white' | 'black' | 'random';
  opponentType: OpponentType;
  botSkillLevel: number;
  timeControlSeconds: number | null;
}
