from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.analysis import router as analysis_router
from app.routes.reports import router as reports_router


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="RepoAnalyzer API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/v1/health", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(analysis_router, prefix="/api/v1")
    app.include_router(reports_router, prefix="/api/v1")
    return app


app = create_app()
