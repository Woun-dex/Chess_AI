# Chess AI Tutor — Backend

Core FastAPI, SQLAlchemy 2.0, python-chess domain logic, and Stockfish/LLM integration.

## Tutor

The tutor graph supports local Ollama:

```env
LLM_PROVIDER=ollama
LLM_MODEL_NAME=gemma2:9b
LLM_BASE_URL=http://localhost:11434
```

Create a session with `POST /api/v1/tutor/sessions`, then send a message with
`POST /api/v1/tutor/sessions/{session_id}/messages`. Use the `/stream` variant
for Server-Sent Events. Messages and graph checkpoints are persisted in
PostgreSQL; lesson context is retrieved from published lessons by concept.

## Authentication and profiles

The API exposes:

- `POST /api/v1/auth/register` to create an account and its default player profile.
- `POST /api/v1/auth/login` to receive a signed bearer access token.
- `GET /api/v1/users/me` to retrieve the authenticated account and profile.
- `PATCH /api/v1/users/me/profile` to update profile preferences.

Game analysis is processed asynchronously by the Celery worker through Redis:

- `POST /api/v1/games/{game_id}/analysis` queues an idempotent analysis job.
- `GET /api/v1/games/{game_id}/analysis` returns queued, running, retrying,
  completed, or dead job state.

The worker retries transient Stockfish failures up to three attempts. Jobs that
exhaust retries remain in the durable `dead` state with their error message for
operator inspection instead of silently disappearing.

Send tokens as `Authorization: Bearer <access_token>`. Set `AUTH_SECRET` to a
long, random value outside development; the default is intentionally only for
local development. The container entrypoint applies pending Alembic migrations
before starting the API or worker, including the initial migration that creates
the user and profile tables.
