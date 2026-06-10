from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, Response

from sheetcut.api.deps import ArtifactsDep, SessionDep, UserDep
from sheetcut.api.schemas import GenerationDetail, GenerationSummary, StepsPage
from sheetcut.core.models import EXCEL_COLUMN_NAMES
from sheetcut.services import GenerationService

router = APIRouter(prefix="/generations", tags=["generations"])

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("")
def list_generations(
    session: SessionDep,
    artifacts: ArtifactsDep,
    _user: UserDep,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[GenerationSummary]:
    svc = GenerationService(session, artifacts)
    return [GenerationSummary.from_row(r) for r in svc.list_all(limit=limit, offset=offset)]


@router.get("/{generation_id}")
def get_generation(
    generation_id: int, session: SessionDep, artifacts: ArtifactsDep, _user: UserDep
) -> GenerationDetail:
    return GenerationDetail.from_row(GenerationService(session, artifacts).get(generation_id))


@router.get("/{generation_id}/steps")
def get_steps(
    generation_id: int,
    session: SessionDep,
    artifacts: ArtifactsDep,
    _user: UserDep,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> StepsPage:
    row = GenerationService(session, artifacts).get(generation_id)
    program = GenerationService.program(row)
    rows = program.rows()
    return StepsPage(
        generation_id=generation_id,
        columns=EXCEL_COLUMN_NAMES,
        rows=rows[offset : offset + limit],
        total_rows=len(rows),
        offset=offset,
        limit=limit,
    )


@router.get("/{generation_id}/artifact.xlsx")
def get_artifact(
    generation_id: int, session: SessionDep, artifacts: ArtifactsDep, _user: UserDep
) -> Response:
    name, payload = GenerationService(session, artifacts).artifact(generation_id)
    return Response(
        content=payload,
        media_type=XLSX_MIME,
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@router.get("/{generation_id}/plot")
def get_plot(
    generation_id: int, session: SessionDep, artifacts: ArtifactsDep, _user: UserDep
) -> dict[str, Any]:
    return GenerationService.plot(GenerationService(session, artifacts).get(generation_id))
