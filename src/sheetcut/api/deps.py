"""FastAPI dependencies: settings, DB sessions, artifact store, auth."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from sheetcut.services import ArtifactStore
from sheetcut.settings import Settings


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def get_session(request: Request) -> Iterator[Session]:
    factory = request.app.state.session_factory
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_artifacts(settings: Annotated[Settings, Depends(get_settings)]) -> ArtifactStore:
    return ArtifactStore(settings.artifacts_dir)


def get_current_user(
    settings: Annotated[Settings, Depends(get_settings)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> str:
    """Auth seam. LAN v1 runs open (no key configured); setting
    SHEETCUT_API_KEY turns on shared-key auth without further code changes.
    Swap this dependency for OIDC/user lookup when multi-user arrives."""
    if settings.api_key is not None and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="invalid or missing X-API-Key")
    return "operator"


SessionDep = Annotated[Session, Depends(get_session)]
ArtifactsDep = Annotated[ArtifactStore, Depends(get_artifacts)]
UserDep = Annotated[str, Depends(get_current_user)]
