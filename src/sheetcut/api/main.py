"""FastAPI application factory.

Serves the JSON API under /api/v1 and, when a built SPA exists at web/dist
(or SHEETCUT_WEB_DIST), the static frontend at /.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from sheetcut import __version__
from sheetcut.api.routers import generations, machine_config, profiles
from sheetcut.core import GenerationError
from sheetcut.db import make_engine, make_session_factory
from sheetcut.services import ConflictError, NotFoundError
from sheetcut.settings import Settings, get_settings


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    engine = make_engine(settings)
    app.state.engine = engine
    app.state.session_factory = make_session_factory(engine)
    yield
    engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="sheetcut", version=__version__, lifespan=_lifespan)
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(NotFoundError)
    async def _not_found(_req: Request, exc: NotFoundError) -> Response:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ConflictError)
    async def _conflict(_req: Request, exc: ConflictError) -> Response:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(GenerationError)
    async def _generation_error(_req: Request, exc: GenerationError) -> Response:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.get("/api/v1/healthz", tags=["meta"])
    def healthz() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    app.include_router(profiles.router, prefix="/api/v1")
    app.include_router(generations.router, prefix="/api/v1")
    app.include_router(machine_config.router, prefix="/api/v1")

    web_dist = Path(os.environ.get("SHEETCUT_WEB_DIST", "web/dist"))
    if web_dist.is_dir():
        app.mount("/", StaticFiles(directory=web_dist, html=True), name="spa")

    return app


def run() -> None:
    import uvicorn

    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
