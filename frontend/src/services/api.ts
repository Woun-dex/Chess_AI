import { AuthToken, CreateGamePayload, GameResponse, GameReview, MakeMovePayload, User } from '../types/chess';

interface AnalysisJobResponse {
  job_id: string;
  game_id: string;
  status: 'queued' | 'running' | 'completed' | 'retrying' | 'dead';
  attempts: number;
  progress: number;
  error_message: string | null;
  result: GameReview | null;
}

export interface HealthResponse {
  status: string;
  environment: string;
  version: string;
}

export const API_BASE = '/api/v1';
const TOKEN_KEY = 'chess-ai-access-token';

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function saveAccessToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

function authHeaders(): HeadersInit {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function errorMessage(response: Response, fallback: string): Promise<string> {
  const errorData = await response.json().catch(() => ({}));
  return errorData.message || errorData.detail || fallback;
}

export async function login(email: string, password: string): Promise<AuthToken> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error(await errorMessage(response, 'Unable to sign in'));
  return response.json();
}

export async function register(email: string, username: string, password: string): Promise<User> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, username, password }),
  });
  if (!response.ok) throw new Error(await errorMessage(response, 'Unable to create account'));
  return response.json();
}

export async function getCurrentUser(): Promise<User> {
  const response = await fetch(`${API_BASE}/users/me`, { headers: authHeaders() });
  if (!response.ok) throw new Error(await errorMessage(response, 'Your session has expired'));
  return response.json();
}

export async function analyzeGame(gameId: string, depth = 16, multipv = 3): Promise<GameReview> {
  const response = await fetch(`${API_BASE}/games/${gameId}/analysis?depth=${depth}&multipv=${multipv}`, {
    method: 'POST',
    headers: authHeaders(),
  });
  if (!response.ok) throw new Error(await errorMessage(response, 'Unable to queue analysis'));

  const job = (await response.json()) as AnalysisJobResponse;
  for (let attempt = 0; attempt < 120; attempt += 1) {
    if (job.status === 'completed' && job.result) return job.result;
    if (job.status === 'dead') throw new Error(job.error_message || 'Analysis failed after retries');
    await new Promise((resolve) => window.setTimeout(resolve, 1000));
    const statusResponse = await fetch(`${API_BASE}/games/${gameId}/analysis`, { headers: authHeaders() });
    if (!statusResponse.ok) throw new Error(await errorMessage(statusResponse, 'Unable to retrieve analysis status'));
    Object.assign(job, (await statusResponse.json()) as AnalysisJobResponse);
  }
  throw new Error('Analysis is taking longer than expected. Please try again shortly.');
}

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
      ...authHeaders(),
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
      ...authHeaders(),
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
  const response = await fetch(`${API_BASE}/games/${gameId}`, { headers: authHeaders() });
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
      ...authHeaders(),
    },
    body: JSON.stringify({ player_id: playerId }),
  });

  if (!response.ok) {
    throw new Error(`Failed to resign game (${response.status})`);
  }

  return response.json();
}
