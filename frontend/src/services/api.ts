import { CreateGamePayload, GameResponse, MakeMovePayload } from '../types/chess';

export interface HealthResponse {
  status: string;
  environment: string;
  version: string;
}

export const API_BASE = '/api/v1';

export async function checkBackendHealth(): Promise<HealthResponse> {
  const response = await fetch('/health');
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json();
}

export async function createGame(payload: CreateGamePayload): Promise<GameResponse> {
  const response = await fetch(`${API_BASE}/games/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || `Failed to create game (${response.status})`);
  }

  return response.json();
}

export async function makeMove(
  gameId: string,
  payload: MakeMovePayload
): Promise<GameResponse> {
  const response = await fetch(`${API_BASE}/games/${gameId}/moves`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': `${gameId}-${payload.expected_version}-${payload.move}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.detail || `Move rejected (${response.status})`);
  }

  return response.json();
}

export async function getGame(gameId: string): Promise<GameResponse> {
  const response = await fetch(`${API_BASE}/games/${gameId}`);
  if (!response.ok) {
    throw new Error(`Failed to retrieve game (${response.status})`);
  }
  return response.json();
}

export async function resignGame(
  gameId: string,
  playerId: string
): Promise<GameResponse> {
  const response = await fetch(`${API_BASE}/games/${gameId}/resign`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ player_id: playerId }),
  });

  if (!response.ok) {
    throw new Error(`Failed to resign game (${response.status})`);
  }

  return response.json();
}
