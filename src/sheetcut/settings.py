"""Runtime configuration via environment variables (SHEETCUT_*)."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SHEETCUT_", env_file=".env", extra="ignore")

    # All persistent state (SQLite DB + generated artifacts) lives under one
    # directory so backup == copy this directory (or the Docker volume).
    data_dir: Path = Path("data")

    # Optional shared API key; when set, mutating/API access requires the
    # X-API-Key header (see sheetcut.api.deps).
    api_key: str | None = None

    cors_origins: list[str] = ["*"]

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.data_dir / 'sheetcut.db'}"

    @property
    def artifacts_dir(self) -> Path:
        return self.data_dir / "artifacts"


def get_settings() -> Settings:
    return Settings()
