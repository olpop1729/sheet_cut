"""Unit tests for the core models and the guard rails around the ports."""

import pytest

from sheetcut.core import (
    CutProfile,
    GenerationError,
    MachineConfig,
    PatternType,
    RunParameters,
    ToolSpec,
    generate,
)
from sheetcut.core.export import plot_series, read_grid, write_xlsx


def _profile(*tools: ToolSpec) -> CutProfile:
    return CutProfile(name="t", tools=list(tools))


def test_unknown_tool_name_rejected() -> None:
    with pytest.raises(ValueError, match="unknown tool name"):
        ToolSpec(name="laser")


def test_pattern_type_inference() -> None:
    assert _profile(ToolSpec(name="fp45")).pattern_type == PatternType.SIDE_LIMB_YOKE
    assert _profile(ToolSpec(name="ys")).pattern_type == PatternType.SPLIT_YOKE
    assert _profile(ToolSpec(name="s")).pattern_type == PatternType.SPEAR_HORIZONTAL
    assert _profile(ToolSpec(name="s", steplap_type=2)).pattern_type == PatternType.FISH_SYMMETRIC
    assert (
        _profile(ToolSpec(name="s", steplap_type=2, is_skewed=True)).pattern_type
        == PatternType.FISH_ASYMMETRIC
    )
    assert _profile(ToolSpec(name="s", steplap_type=3)).pattern_type == PatternType.FISH_ASYMMETRIC


def test_split_yoke_unsupported() -> None:
    profile = _profile(ToolSpec(name="ys"))
    with pytest.raises(GenerationError, match="split-yoke"):
        generate(profile, RunParameters(length_list=[100.0]), MachineConfig())


def test_sly_length_count_validated() -> None:
    profile = _profile(ToolSpec(name="fp45"), ToolSpec(name="h"), ToolSpec(name="fm45"))
    with pytest.raises(GenerationError, match="lengths"):
        generate(profile, RunParameters(length_list=[100.0]), MachineConfig())


def test_sly_missing_steplap_distances_rejected() -> None:
    profile = _profile(
        ToolSpec(name="fp45", steplap_type=1, steplap_count=5, open_code=1),
        ToolSpec(name="h"),
        ToolSpec(name="fm45", steplap_type=1, steplap_count=5, open_code=2),
    )
    with pytest.raises(GenerationError, match="step-lap distances"):
        generate(profile, RunParameters(length_list=[500.0, 500.0]), MachineConfig())


def test_spear_h_layers_with_holes_rejected() -> None:
    profile = _profile(
        ToolSpec(name="s", steplap_type=1, steplap_count=3, open_code=1),
        ToolSpec(name="h"),
    )
    params = RunParameters(
        length_list=[400.0, 300.0], steplap_distances=[2.0], layers=2, scrap_length=5.0
    )
    with pytest.raises(GenerationError, match="layers=1"):
        generate(profile, params, MachineConfig())


def test_legacy_profile_round_trip() -> None:
    profile = _profile(
        ToolSpec(name="fp45", steplap_type=1, steplap_count=5, open_code=1),
        ToolSpec(name="h"),
        ToolSpec(name="fm45", steplap_type=1, steplap_count=5, open_code=2),
    )
    again = CutProfile.from_legacy_data(profile.to_legacy_data(), name="t")
    assert again.tools == profile.tools


def test_generate_and_exports_work_end_to_end() -> None:
    profile = _profile(
        ToolSpec(name="fp45", steplap_type=1, steplap_count=3, open_code=1),
        ToolSpec(name="h"),
        ToolSpec(name="v", steplap_type=2, steplap_count=3, open_code=1),
        ToolSpec(name="h"),
        ToolSpec(name="fm45", steplap_type=1, steplap_count=3, open_code=2),
    )
    params = RunParameters(
        length_list=[700.0, 900.0, 900.0, 700.0], steplap_distances=[2.0, 1.0, 2.0]
    )
    program = generate(profile, params, MachineConfig())
    assert program.pattern_length is not None and program.pattern_length > 0
    assert program.sheet_count and program.sheet_count[0] > 0
    assert len(program.feed) == program.end_index[0]

    grid = read_grid(write_xlsx(program))
    assert grid[0][1] == "Feed Dist"
    assert len(grid) == program.row_count + 1

    series = plot_series(program, MachineConfig())
    assert len(series["events"]) == len(program.feed)
    positions = [e["position"] for e in series["events"]]
    assert positions == sorted(positions)

    # sheet-view geometry: cut_x = position minus the tool's distance from
    # the v-notch; SLY v events carry no per-row traverse (legacy truncation)
    assert series["distances"]["shear"] == 4334.5
    for event in series["events"]:
        if event["kind"] == "shear":
            assert event["cut_x"] == round(event["position"] - 4334.5, 5)
        elif event["kind"] == "hole":
            assert event["cut_x"] == round(event["position"] - 1250.0, 5)
        elif event["kind"] == "vnotch":
            assert event["cut_x"] == event["position"]
            assert event["v_travel"] is None
    assert {e["kind"] for e in series["events"]} == {"shear", "hole", "vnotch"}


def test_plot_series_spear_h_v_travel_is_per_row() -> None:
    profile = _profile(
        ToolSpec(name="s", steplap_type=1, steplap_count=3, open_code=1),
        ToolSpec(name="h"),
    )
    params = RunParameters(length_list=[400.0, 300.0], steplap_distances=[2.0], scrap_length=5.0)
    program = generate(profile, params, MachineConfig())
    series = plot_series(program, MachineConfig())
    v_events = [e for e in series["events"] if e["kind"] == "vnotch"]
    assert v_events and all(e["v_travel"] == 5.0 for e in v_events)
