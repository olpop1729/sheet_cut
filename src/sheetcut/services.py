"""Use-case layer shared by the HTTP API and the MCP server.

Every interface adapter (FastAPI router, MCP tool, future CLI) goes through
these services; none of them touch ``sheetcut.core`` or the ORM directly.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sheetcut.core import (
    CutProfile,
    CutProgram,
    MachineConfig,
    RunParameters,
    ToolSpec,
    generate,
)
from sheetcut.core.export import plot_series, write_xlsx
from sheetcut.db import GenerationRow, MachineConfigRow, ProfileRow


class NotFoundError(LookupError):
    pass


class ConflictError(ValueError):
    pass


class ArtifactStore:
    """Filesystem artifact storage; swappable for object storage later."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, name: str, payload: bytes) -> str:
        path = self.root / name
        path.write_bytes(payload)
        return name

    def read(self, name: str) -> bytes:
        path = self.root / name
        if not path.is_file():
            raise NotFoundError(f"artifact {name!r} not found")
        return path.read_bytes()


class ProfileService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[ProfileRow]:
        return list(self.session.scalars(select(ProfileRow).order_by(ProfileRow.id)))

    def get(self, profile_id: int) -> ProfileRow:
        row = self.session.get(ProfileRow, profile_id)
        if row is None:
            raise NotFoundError(f"profile {profile_id} not found")
        return row

    def create(self, name: str, tools: list[ToolSpec]) -> ProfileRow:
        # Validates the tool sequence through the domain model first.
        profile = CutProfile(name=name, tools=tools)
        row = ProfileRow(name=name, tools=[t.model_dump() for t in profile.tools])
        self.session.add(row)
        try:
            self.session.flush()
        except IntegrityError as err:
            self.session.rollback()
            raise ConflictError(f"profile name {name!r} already exists") from err
        return row

    def update(self, profile_id: int, name: str, tools: list[ToolSpec]) -> ProfileRow:
        row = self.get(profile_id)
        profile = CutProfile(name=name, tools=tools)
        row.name = name
        row.tools = [t.model_dump() for t in profile.tools]
        try:
            self.session.flush()
        except IntegrityError as err:
            self.session.rollback()
            raise ConflictError(f"profile name {name!r} already exists") from err
        return row

    def delete(self, profile_id: int) -> None:
        self.session.delete(self.get(profile_id))
        self.session.flush()

    @staticmethod
    def to_domain(row: ProfileRow) -> CutProfile:
        return CutProfile(name=row.name, tools=[ToolSpec(**t) for t in row.tools])


class MachineConfigService:
    SEED_COMMENT = "seeded with the legacy gui/config.json calibration"

    def __init__(self, session: Session) -> None:
        self.session = session

    def ensure_seeded(self) -> None:
        if self.session.scalars(select(MachineConfigRow.id).limit(1)).first() is None:
            self.session.add(
                MachineConfigRow(config=MachineConfig().model_dump(), comment=self.SEED_COMMENT)
            )
            self.session.flush()

    def current_row(self) -> MachineConfigRow:
        self.ensure_seeded()
        row = self.session.scalars(
            select(MachineConfigRow).order_by(MachineConfigRow.id.desc()).limit(1)
        ).first()
        assert row is not None
        return row

    def current(self) -> MachineConfig:
        return MachineConfig(**self.current_row().config)

    def update(self, config: MachineConfig, comment: str = "") -> MachineConfigRow:
        row = MachineConfigRow(config=config.model_dump(), comment=comment)
        self.session.add(row)
        self.session.flush()
        return row

    def history(self) -> list[MachineConfigRow]:
        self.ensure_seeded()
        return list(
            self.session.scalars(select(MachineConfigRow).order_by(MachineConfigRow.id.desc()))
        )


class GenerationService:
    def __init__(self, session: Session, artifacts: ArtifactStore) -> None:
        self.session = session
        self.artifacts = artifacts

    def generate_for_profile(self, profile_id: int, params: RunParameters) -> GenerationRow:
        profile_row = ProfileService(self.session).get(profile_id)
        profile = ProfileService.to_domain(profile_row)
        config_row = MachineConfigService(self.session).current_row()
        config = MachineConfig(**config_row.config)

        program = generate(profile, params, config)  # raises GenerationError on bad input

        row = GenerationRow(
            profile_id=profile_row.id,
            profile_name=profile_row.name,
            pattern_type=int(program.pattern_type),
            profile_snapshot=profile.model_dump(),
            parameters=params.model_dump(),
            machine_config=config.model_dump(),
            program=program.model_dump(),
        )
        self.session.add(row)
        self.session.flush()
        row.artifact_path = self.artifacts.write(
            f"gen_{row.id:06d}_{_safe_name(profile_row.name)}.xlsx", write_xlsx(program)
        )
        self.session.flush()
        return row

    def get(self, generation_id: int) -> GenerationRow:
        row = self.session.get(GenerationRow, generation_id)
        if row is None:
            raise NotFoundError(f"generation {generation_id} not found")
        return row

    def list_all(self, limit: int = 50, offset: int = 0) -> list[GenerationRow]:
        return list(
            self.session.scalars(
                select(GenerationRow).order_by(GenerationRow.id.desc()).limit(limit).offset(offset)
            )
        )

    def artifact(self, generation_id: int) -> tuple[str, bytes]:
        row = self.get(generation_id)
        if not row.artifact_path:
            raise NotFoundError(f"generation {generation_id} has no artifact")
        return row.artifact_path, self.artifacts.read(row.artifact_path)

    @staticmethod
    def program(row: GenerationRow) -> CutProgram:
        return CutProgram(**row.program)

    @classmethod
    def plot(cls, row: GenerationRow) -> dict[str, object]:
        return plot_series(cls.program(row), MachineConfig(**row.machine_config))


def _safe_name(name: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    return cleaned[:60] or "profile"
