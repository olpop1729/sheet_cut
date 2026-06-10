"""Request/response schemas for the HTTP API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from sheetcut.core import MachineConfig, RunParameters, ToolSpec
from sheetcut.db import GenerationRow, MachineConfigRow, ProfileRow
from sheetcut.services import GenerationService


class ProfileIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    tools: list[ToolSpec] = Field(min_length=1)


class ProfileOut(BaseModel):
    id: int
    name: str
    tools: list[ToolSpec]
    pattern_type: int
    steplap_tool_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: ProfileRow) -> ProfileOut:
        from sheetcut.services import ProfileService

        domain = ProfileService.to_domain(row)
        return cls(
            id=row.id,
            name=row.name,
            tools=domain.tools,
            pattern_type=int(domain.pattern_type),
            steplap_tool_count=domain.steplap_tool_count,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class GenerateIn(RunParameters):
    pass


class GenerationSummary(BaseModel):
    id: int
    profile_id: int | None
    profile_name: str
    pattern_type: int
    parameters: dict[str, Any]
    row_count: int
    pattern_length: float | None
    sheet_count: int | None
    artifact_path: str | None
    created_at: datetime

    @classmethod
    def from_row(cls, row: GenerationRow) -> GenerationSummary:
        program = GenerationService.program(row)
        return cls(
            id=row.id,
            profile_id=row.profile_id,
            profile_name=row.profile_name,
            pattern_type=row.pattern_type,
            parameters=row.parameters,
            row_count=program.row_count,
            pattern_length=program.pattern_length,
            sheet_count=program.sheet_count[0] if program.sheet_count else None,
            artifact_path=row.artifact_path,
            created_at=row.created_at,
        )


class StepsPage(BaseModel):
    generation_id: int
    columns: list[str]
    rows: list[list[Any]]
    total_rows: int
    offset: int
    limit: int


class GenerationDetail(GenerationSummary):
    profile_snapshot: dict[str, Any]
    machine_config: dict[str, Any]
    start_index: int | None
    end_index: int | None

    @classmethod
    def from_row(cls, row: GenerationRow) -> GenerationDetail:
        program = GenerationService.program(row)
        base = GenerationSummary.from_row(row)
        return cls(
            **base.model_dump(),
            profile_snapshot=row.profile_snapshot,
            machine_config=row.machine_config,
            start_index=program.start_index[0] if program.start_index else None,
            end_index=program.end_index[0] if program.end_index else None,
        )


class MachineConfigIn(MachineConfig):
    comment: str = Field(default="", max_length=500)


class MachineConfigOut(BaseModel):
    version: int
    config: MachineConfig
    comment: str
    created_at: datetime

    @classmethod
    def from_row(cls, row: MachineConfigRow) -> MachineConfigOut:
        return cls(
            version=row.id,
            config=MachineConfig(**row.config),
            comment=row.comment,
            created_at=row.created_at,
        )
