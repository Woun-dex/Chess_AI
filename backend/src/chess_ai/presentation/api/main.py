from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from chess_ai.config import get_settings
from chess_ai.domain.models.game import (
    ConcurrencyConflictError,
    GameNotInProgressError,
    IllegalMoveError,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Startup initialization (e.g. pool warmup, engine binary check)
    _ = get_settings()
    yield
    # Graceful shutdown (e.g. terminate engine pool, close db connection pool)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Domain Exception Mappings
    @app.exception_handler(IllegalMoveError)
    async def illegal_move_handler(_request: Request, exc: IllegalMoveError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "ILLEGAL_MOVE", "message": str(exc)},
        )

    @app.exception_handler(ConcurrencyConflictError)
    async def concurrency_handler(_request: Request, exc: ConcurrencyConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": "CONCURRENCY_CONFLICT", "message": str(exc)},
        )

    @app.exception_handler(GameNotInProgressError)
    async def game_finished_handler(_request: Request, exc: GameNotInProgressError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "GAME_FINISHED", "message": str(exc)},
        )

    # Routers
    from chess_ai.presentation.api.routes.games import router as games_router

    app.include_router(games_router)

    @app.get("/health", tags=["System"])
    async def health_check() -> dict[str, str]:
        return {
            "status": "healthy",
            "environment": settings.APP_ENV,
            "version": "0.1.0",
        }

    return app


app = create_app()
