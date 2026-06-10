"""MCP server exposing sheetcut to AI clients (Claude Desktop/Code, agents).

Runs against the same database/artifact volume as the HTTP API by calling the
service layer in-process. Default transport is stdio; set
SHEETCUT_MCP_TRANSPORT=streamable-http to serve over the network on a LAN.

Tools are thin wrappers around ``SheetcutTools`` methods so the logic stays
directly unit-testable without an MCP transport.
"""

from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from sheetcut.api.schemas import GenerationSummary, MachineConfigOut, ProfileOut
from sheetcut.core import CutProfile, RunParameters, ToolSpec
from sheetcut.core.models import EXCEL_COLUMN_NAMES
from sheetcut.db import make_engine, make_session_factory, session_scope
from sheetcut.services import (
    ArtifactStore,
    GenerationService,
    MachineConfigService,
    ProfileService,
)
from sheetcut.settings import Settings, get_settings


class SheetcutTools:
    """Tool implementations bound to a database; one short session per call."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.factory = make_session_factory(make_engine(settings))
        self.artifacts = ArtifactStore(settings.artifacts_dir)

    def list_profiles(self) -> list[dict[str, Any]]:
        with session_scope(self.factory) as session:
            rows = ProfileService(session).list_all()
            return [ProfileOut.from_row(r).model_dump(mode="json") for r in rows]

    def get_profile(self, profile_id: int) -> dict[str, Any]:
        with session_scope(self.factory) as session:
            return ProfileOut.from_row(ProfileService(session).get(profile_id)).model_dump(
                mode="json"
            )

    def create_profile(self, name: str, tools: list[dict[str, Any]]) -> dict[str, Any]:
        specs = [ToolSpec(**t) for t in tools]
        with session_scope(self.factory) as session:
            row = ProfileService(session).create(name, specs)
            return ProfileOut.from_row(row).model_dump(mode="json")

    def validate_profile(self, tools: list[dict[str, Any]]) -> dict[str, Any]:
        try:
            profile = CutProfile(name="candidate", tools=[ToolSpec(**t) for t in tools])
        except ValueError as err:
            return {"valid": False, "errors": [str(err)], "warnings": []}
        warnings = []
        for i, tool in enumerate(profile.tools):
            if tool.steplap_count > 1 and tool.steplap_count % 2 == 0:
                warnings.append(
                    f"tool {i + 1} ({tool.name}): even step-lap count "
                    f"{tool.steplap_count}; the machine workflow normally uses odd counts"
                )
            if tool.steplap_count > 9:
                warnings.append(
                    f"tool {i + 1} ({tool.name}): high step-lap count may affect accuracy"
                )
        if profile.pattern_type == 2:
            warnings.append("split-yoke profiles cannot be generated in v1")
        return {
            "valid": True,
            "pattern_type": int(profile.pattern_type),
            "steplap_tool_count": profile.steplap_tool_count,
            "errors": [],
            "warnings": warnings,
        }

    def generate_cut_program(
        self,
        profile_id: int,
        length_list: list[float],
        steplap_distances: list[float] | None = None,
        layers: int = 1,
        start_sheet: int = 1,
        scrap_length: float = 0.0,
    ) -> dict[str, Any]:
        params = RunParameters(
            length_list=length_list,
            steplap_distances=steplap_distances or [],
            layers=layers,
            start_sheet=start_sheet,
            scrap_length=scrap_length,
        )
        with session_scope(self.factory) as session:
            row = GenerationService(session, self.artifacts).generate_for_profile(
                profile_id, params
            )
            return GenerationSummary.from_row(row).model_dump(mode="json")

    def list_generations(self, limit: int = 20) -> list[dict[str, Any]]:
        with session_scope(self.factory) as session:
            rows = GenerationService(session, self.artifacts).list_all(limit=limit)
            return [GenerationSummary.from_row(r).model_dump(mode="json") for r in rows]

    def get_cut_program_steps(
        self, generation_id: int, offset: int = 0, limit: int = 100
    ) -> dict[str, Any]:
        with session_scope(self.factory) as session:
            row = GenerationService(session, self.artifacts).get(generation_id)
            program = GenerationService.program(row)
            rows = program.rows()
            return {
                "generation_id": generation_id,
                "columns": EXCEL_COLUMN_NAMES,
                "rows": rows[offset : offset + limit],
                "total_rows": len(rows),
                "offset": offset,
                "limit": limit,
            }

    def get_machine_config(self) -> dict[str, Any]:
        with session_scope(self.factory) as session:
            return MachineConfigOut.from_row(
                MachineConfigService(session).current_row()
            ).model_dump(mode="json")

    def read_artifact(self, generation_id: int) -> bytes:
        with session_scope(self.factory) as session:
            _, payload = GenerationService(session, self.artifacts).artifact(generation_id)
            return payload


def build_server(settings: Settings | None = None) -> FastMCP:
    tools = SheetcutTools(settings or get_settings())
    mcp = FastMCP(
        "sheetcut",
        instructions=(
            "Generate CNC cut-feed programs for transformer core laminations. "
            "Workflow: validate_profile -> create_profile -> generate_cut_program "
            "-> get_cut_program_steps; the .xlsx the operator loads on the machine "
            "is at resource sheetcut://generations/{id}/artifact.xlsx. "
            "Pattern types: 1 side-limb yoke, 3 spear/central limb, "
            "4 symmetric fish, 5 asymmetric fish."
        ),
    )

    mcp.tool(description="List saved cut profiles")(tools.list_profiles)
    mcp.tool(description="Get one cut profile by id")(tools.get_profile)
    mcp.tool(
        description=(
            "Create a cut profile. Each tool: name (fm45|fp45|f0|v|h|s|ys), "
            "steplap_type (0 none, 1 horizontal, 2 vertical, 3 skewed), "
            "steplap_count, open_code (0 NA, 1 open, 2 closed, 3-10 front/rear "
            "combinations), is_skewed"
        )
    )(tools.create_profile)
    mcp.tool(description="Validate a tool sequence without saving; returns warnings")(
        tools.validate_profile
    )
    mcp.tool(
        description=(
            "Generate a cut program for a profile. length_list are segment lengths "
            "in mm (len(tools)-1 entries for side-limb yokes); steplap_distances one "
            "per tool with steplap_count>1; scrap_length only for pattern type 3"
        )
    )(tools.generate_cut_program)
    mcp.tool(description="List recent generations")(tools.list_generations)
    mcp.tool(description="Page through the generated step table")(tools.get_cut_program_steps)
    mcp.tool(description="Get the active machine calibration")(tools.get_machine_config)

    @mcp.resource("sheetcut://generations/{generation_id}/artifact.xlsx")
    def artifact(generation_id: int) -> bytes:
        return tools.read_artifact(generation_id)

    return mcp


def main() -> None:
    transport = os.environ.get("SHEETCUT_MCP_TRANSPORT", "stdio")
    server = build_server()
    if transport == "streamable-http":
        server.run(transport="streamable-http")
    else:
        server.run()
