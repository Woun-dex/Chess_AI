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
