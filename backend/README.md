# Chess AI Tutor — Backend

Core FastAPI, SQLAlchemy 2.0, python-chess domain logic, and Stockfish/LLM integration.

## Authentication and profiles

The API exposes:

- `POST /api/v1/auth/register` to create an account and its default player profile.
- `POST /api/v1/auth/login` to receive a signed bearer access token.
- `GET /api/v1/users/me` to retrieve the authenticated account and profile.
- `PATCH /api/v1/users/me/profile` to update profile preferences.

Send tokens as `Authorization: Bearer <access_token>`. Set `AUTH_SECRET` to a
long, random value outside development; the default is intentionally only for
local development. User and profile tables are created by the initial Alembic
migration.
