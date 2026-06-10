"""MCP tool-layer tests (logic level; transport is the SDK's concern)."""

from pathlib import Path

import pytest

from sheetcut.mcp_server.server import SheetcutTools, build_server
from sheetcut.settings import Settings

SLY_TOOLS = [
    {"name": "fp45", "steplap_type": 1, "steplap_count": 3, "open_code": 1},
    {"name": "h"},
    {"name": "v", "steplap_type": 2, "steplap_count": 3, "open_code": 1},
    {"name": "h"},
    {"name": "fm45", "steplap_type": 1, "steplap_count": 3, "open_code": 2},
]


@pytest.fixture
def tools(tmp_path: Path) -> SheetcutTools:
    return SheetcutTools(Settings(data_dir=tmp_path / "data"))


def test_full_workflow(tools: SheetcutTools) -> None:
    verdict = tools.validate_profile(SLY_TOOLS)
    assert verdict["valid"] and verdict["pattern_type"] == 1 and not verdict["warnings"]

    profile = tools.create_profile("yoke-a", SLY_TOOLS)
    assert tools.list_profiles()[0]["id"] == profile["id"]
    assert tools.get_profile(profile["id"])["name"] == "yoke-a"

    summary = tools.generate_cut_program(
        profile["id"],
        length_list=[700.0, 900.0, 900.0, 700.0],
        steplap_distances=[2.0, 1.0, 2.0],
    )
    assert summary["pattern_type"] == 1
    assert summary["row_count"] > 0
    assert tools.list_generations()[0]["id"] == summary["id"]

    steps = tools.get_cut_program_steps(summary["id"], limit=4)
    assert steps["columns"][0] == "Feed Dist"
    assert len(steps["rows"]) == 4

    config = tools.get_machine_config()
    assert config["config"]["distance_shear_vnotch"] == 4334.5

    artifact = tools.read_artifact(summary["id"])
    assert artifact[:2] == b"PK"


def test_validate_reports_problems(tools: SheetcutTools) -> None:
    bad = tools.validate_profile([{"name": "laser"}])
    assert not bad["valid"] and bad["errors"]

    even = tools.validate_profile(
        [
            {"name": "fp45", "steplap_type": 1, "steplap_count": 4, "open_code": 1},
            {"name": "h"},
            {"name": "fm45", "steplap_type": 1, "steplap_count": 4, "open_code": 2},
        ]
    )
    assert even["valid"] and any("even step-lap" in w for w in even["warnings"])

    split = tools.validate_profile([{"name": "ys"}])
    assert any("split-yoke" in w for w in split["warnings"])


def test_server_builds_and_registers_tools(tmp_path: Path) -> None:
    import anyio

    server = build_server(Settings(data_dir=tmp_path / "data"))
    names = {t.name for t in anyio.run(server.list_tools)}
    assert {
        "list_profiles",
        "create_profile",
        "validate_profile",
        "generate_cut_program",
        "get_cut_program_steps",
        "get_machine_config",
    } <= names
