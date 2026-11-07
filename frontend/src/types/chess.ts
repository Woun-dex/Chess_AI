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

export interface UserProfile {
  id: string;
  user_id: string;
  preferred_color: Color;
  classical_rating: number;
  blitz_rating: number;
  rapid_rating: number;
  games_played: number;
  wins: number;
  losses: number;
  draws: number;
  favorite_opening_as_white: string | null;
  favorite_opening_as_black: string | null;
}

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  profile: UserProfile;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface AnalysisVariation {
  rank: number;
  centipawns: number | null;
  mate_in: number | null;
  best_move_uci: string;
  pv: string[];
}

export interface PositionEvaluation {
  fen: string;
  centipawns: number | null;
  mate_in: number | null;
  best_move_uci: string;
  pv: string[];
  depth: number;
  variations: AnalysisVariation[];
}

export interface MoveAnalysis {
  move_number: number;
  color: Color;
  move_uci: string;
  move_san: string;
  classification: MoveClassification;
  centipawn_loss: number;
  score_before: PositionEvaluation;
  score_after: PositionEvaluation;
  tactical_motifs: string[];
}

export interface GameReview {
  depth: number;
  multipv: number;
  final_evaluation: PositionEvaluation;
  moves: MoveAnalysis[];
  classification_counts: Record<string, number>;
  accuracy: Record<Color, number>;
  critical_moments: number[];
  summary: string;
}
