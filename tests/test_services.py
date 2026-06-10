"""Service-layer tests over a temporary SQLite database."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from sheetcut.core import GenerationError, MachineConfig, RunParameters, ToolSpec
from sheetcut.db import make_engine, make_session_factory
from sheetcut.services import (
    ArtifactStore,
    ConflictError,
    GenerationService,
    MachineConfigService,
    NotFoundError,
    ProfileService,
)
from sheetcut.settings import Settings

SLY_TOOLS = [
    ToolSpec(name="fp45", steplap_type=1, steplap_count=3, open_code=1),
    ToolSpec(name="h"),
    ToolSpec(name="v", steplap_type=2, steplap_count=3, open_code=1),
    ToolSpec(name="h"),
    ToolSpec(name="fm45", steplap_type=1, steplap_count=3, open_code=2),
]

SLY_PARAMS = RunParameters(
    length_list=[700.0, 900.0, 900.0, 700.0], steplap_distances=[2.0, 1.0, 2.0]
)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(data_dir=tmp_path / "data")


@pytest.fixture
def session(settings: Settings) -> Iterator[Session]:
    factory = make_session_factory(make_engine(settings))
    with factory() as s:
        yield s


@pytest.fixture
def artifacts(settings: Settings) -> ArtifactStore:
    return ArtifactStore(settings.artifacts_dir)


def test_profile_crud(session: Session) -> None:
    svc = ProfileService(session)
    row = svc.create("yoke-a", SLY_TOOLS)
    assert row.id is not None
    assert row.tools[0]["name"] == "fp45"
    session.commit()  # conflicts roll the transaction back; persist first

    with pytest.raises(ConflictError):
        svc.create("yoke-a", SLY_TOOLS)

    svc.update(row.id, "yoke-b", SLY_TOOLS)
    assert svc.get(row.id).name == "yoke-b"
    assert len(svc.list_all()) == 1

    svc.delete(row.id)
    with pytest.raises(NotFoundError):
        svc.get(row.id)


def test_machine_config_seed_and_history(session: Session) -> None:
    svc = MachineConfigService(session)
    current = svc.current()
    assert current == MachineConfig()  # seeded with legacy calibration

    svc.update(MachineConfig(offset_fp45=0.8), comment="recalibrated +45 shear")
    assert svc.current().offset_fp45 == 0.8
    history = svc.history()
    assert len(history) == 2
    assert history[0].comment == "recalibrated +45 shear"
    assert history[-1].comment == MachineConfigService.SEED_COMMENT


def test_generation_end_to_end(session: Session, artifacts: ArtifactStore) -> None:
    profile = ProfileService(session).create("yoke-a", SLY_TOOLS)
    svc = GenerationService(session, artifacts)

    row = svc.generate_for_profile(profile.id, SLY_PARAMS)
    assert row.pattern_type == 1
    assert row.artifact_path and row.artifact_path.endswith(".xlsx")

    name, payload = svc.artifact(row.id)
    assert name == row.artifact_path
    assert payload[:2] == b"PK"  # xlsx zip magic

    program = GenerationService.program(row)
    assert program.row_count > 0
    plot = GenerationService.plot(row)
    assert plot["events"]

    # The snapshot keeps the generation reproducible after profile deletion.
    ProfileService(session).delete(profile.id)
    session.commit()
    assert svc.get(row.id).profile_snapshot["tools"][0]["name"] == "fp45"


def test_generation_propagates_domain_errors(session: Session, artifacts: ArtifactStore) -> None:
    profile = ProfileService(session).create("yoke-a", SLY_TOOLS)
    svc = GenerationService(session, artifacts)
    with pytest.raises(GenerationError):
        svc.generate_for_profile(
            profile.id, RunParameters(length_list=[1.0], steplap_distances=[2.0, 1.0, 2.0])
        )
    with pytest.raises(NotFoundError):
        svc.generate_for_profile(9999, SLY_PARAMS)
