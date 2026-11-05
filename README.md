# Chess AI Tutor 

> **Production-grade chess tutoring platform combining deterministic Stockfish 16 engine calculations with pedagogical LLM coaching.**

---

## 🏛️ The Cardinal Architectural Rule
> **Stockfish is the single authority for chess calculations; the LLM is responsible solely for teaching, explanations, and coaching.**



## 🚀 Quickstart

### Prerequisites
- Docker & Docker Compose
- Or locally: Python 3.12+ (managed by `uv`) and Node.js 20+

### Running via Docker Compose (Recommended)
```bash
# Start all services (PostgreSQL, Redis, FastAPI backend, Worker, Vite frontend)
docker compose up --build
```
- **Frontend**: http://localhost:5173
- **FastAPI Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health


## 🧪 Testing & Code Quality

```bash
# Run backend test suite
make test

# Run linter and typechecker
make lint

# Auto-format codebase
make format
```

