# Chess AI Tutor ♟️🤖

> **Production-grade chess tutoring platform combining deterministic Stockfish 16 engine calculations with pedagogical LLM coaching.**

---

## 🏛️ The Cardinal Architectural Rule
> **Stockfish is the single authority for chess calculations; the LLM is responsible solely for teaching, explanations, and coaching.**
>
> Under no circumstances does an LLM independently calculate legal moves, evaluate positions, or suggest the "best" move without validation from the chess engine.

---

## 🛠️ Technology Stack & Purpose

| Layer | Technology | Architectural Purpose |
|---|---|---|
| **Frontend** | React 18 + TypeScript | Type-safe, component-driven UI |
| **Styling** | Tailwind CSS | Utility-first styling & design system |
| **Chess Rules** | `python-chess` | Server-side legal moves, FEN, PGN parsing |
| **Engine** | Stockfish (UCI Protocol) | Superhuman position evaluation & blunder detection |
| **Backend** | FastAPI + Pydantic v2 | High-throughput asynchronous REST & SSE APIs |
| **Architecture** | Hexagonal / Clean Architecture | Domain core isolated from databases and external APIs |
| **Database** | PostgreSQL 16 + SQLAlchemy 2.0 | Transactional persistence with Unit of Work pattern |
| **Migrations** | Alembic | Version-controlled database schema evolutions |
| **Cache & Queue**| Redis 7 | Distributed locking, idempotency cache, task queue broker |
| **Workers** | Async Worker Pool | Dedicated CPU-bounded engine evaluation processes |
| **Package Manager**| Astral `uv` | Instantaneous Python virtual environment & dependency management |
| **Dev Environment**| Docker Compose | Reproducible multi-service local environment |
| **Quality** | Ruff, MyPy, Pytest, Vitest | Strict static analysis, 100% type safety, test suites |

---

## 📁 Repository Structure

```
Chess_AI/
├── .github/
│   └── workflows/
│       └── ci.yml               # CI Pipeline: Linting, Typechecking, Pytest
├── docs/
│   ├── architecture/
│   │   └── ARCHITECTURE.md      # C4 Context, Domain Invariants, Async Life-cycle
│   └── adr/
│       └── 0001-engine-llm-separation.md
├── backend/
│   ├── src/chess_ai/
│   │   ├── domain/              # Pure domain logic (Game, MoveRecord, Invariants)
│   │   │   ├── models/
│   │   │   └── ports/           # EnginePort, LLMPort, GameRepositoryPort, UnitOfWork
│   │   ├── application/         # Use Cases & CQRS handlers
│   │   ├── infrastructure/      # SQLAlchemy, Stockfish UCI, Redis, LLM adapters
│   │   ├── presentation/        # FastAPI routers, middleware, exception handlers
│   │   └── config.py            # Typed settings via pydantic-settings
│   ├── tests/
│   │   └── unit/                # Pytest unit tests
│   ├── pyproject.toml           # uv / PEP 621 dependencies
│   ├── ruff.toml                # Ruff lint & format rules
│   └── Dockerfile               # Backend container with Stockfish installed
├── frontend/
│   ├── src/
│   │   ├── components/          # ChessBoard, EvalBar, TutorCoach, Header
│   │   ├── services/            # Typed API client
│   │   ├── types/               # TypeScript domain interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml           # Local dev orchestrator (DB, Redis, Backend, Frontend, Worker)
├── Makefile                     # Developer ergonomics (`make dev`, `make test`, `make lint`)
└── README.md
```

---

## 🚀 Quickstart

### Prerequisites
- Docker & Docker Compose
- Or locally: Python 3.12+ (managed by `uv`) and Node.js 20+

### Option A: Running via Docker Compose (Recommended)
```bash
# Start all services (PostgreSQL, Redis, FastAPI backend, Worker, Vite frontend)
docker compose up --build
```
- **Frontend**: http://localhost:5173
- **FastAPI Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Option B: Local Development with `uv`
```bash
# 1. Backend setup
cd backend
../.bin/uv venv
../.bin/uv pip install -e ".[dev]"
../.bin/uv run pytest tests/
../.bin/uv run uvicorn chess_ai.presentation.api.main:app --reload

# 2. Frontend setup
cd ../frontend
npm install
npm run dev
```

---

## 🧪 Testing & Code Quality

```bash
# Run backend test suite
make test

# Run linter and typechecker
make lint

# Auto-format codebase
make format
```

