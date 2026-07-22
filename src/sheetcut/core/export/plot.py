"""Plot-series JSON for client-side visualization.

Derives, from a generated program, everything a client needs to render both
legacy views without re-implementing machine math:

- the coil-position strip (cumulative feed per row), and
- the sheet view (port of ``legacy/gui/visualize.py``): each cut's position
  in sheet space is the accumulated feed minus that tool's distance from the
  V-notch (shear/hole distances come from the machine calibration; the
  V-notch itself is the origin). Sub-mm shear offsets are calibration for the
  machine, not geometry — the legacy visualizer ignored them and so do we.

V-notch traverse per event: for patterns 3/4/5 the legacy table's
``Vnotch Trav Dist`` column aligns row-for-row with operations, so the value
is exact. For side-limb yokes the legacy writer truncated that column to one
entry per step-lap level with no per-row mapping (the old verify screen
showed misaligned values there); we report ``None`` rather than guess, and
clients fall back to a centered notch.
"""

from __future__ import annotations

from typing import Any

from sheetcut.core.models import CutProgram, MachineConfig, PatternType


def plot_series(program: CutProgram, config: MachineConfig | None = None) -> dict[str, Any]:
    config = config or MachineConfig()
    per_row_v_axis = program.pattern_type in (
        PatternType.SPEAR_HORIZONTAL,
        PatternType.FISH_SYMMETRIC,
        PatternType.FISH_ASYMMETRIC,
    )

    position = 0.0
    events: list[dict[str, Any]] = []
    for i, feed in enumerate(program.feed):
        position = round(position + feed, 5)
        tool = program.operation[i] if i < len(program.operation) else None

        kind: str | None = None
        cut_x: float | None = None
        v_travel: float | None = None
        if tool in ("fp45", "fm45", "f0"):
            kind = "shear"
            cut_x = round(position - config.distance_shear_vnotch, 5)
        elif tool == "h":
            kind = "hole"
            cut_x = round(position - config.distance_hole_vnotch, 5)
        elif tool == "v":
            kind = "vnotch"
            cut_x = position
            if per_row_v_axis and i < len(program.v_axis):
                v_travel = program.v_axis[i]

        events.append(
            {
                "row": i + 1,
                "tool": tool,
                "tool_number": (program.tool_number[i] if i < len(program.tool_number) else None),
                "feed": feed,
                "position": position,
                "kind": kind,
                "cut_x": cut_x,
                "v_travel": v_travel,
            }
        )

    return {
        "pattern_type": int(program.pattern_type),
        "pattern_length": program.pattern_length,
        "start_index": program.start_index[0] if program.start_index else None,
        "end_index": program.end_index[0] if program.end_index else None,
        "sheet_count": program.sheet_count[0] if program.sheet_count else None,
        "v_axis": list(program.v_axis),
        "distances": {
            "shear": config.distance_shear_vnotch,
            "hole": config.distance_hole_vnotch,
            "vnotch": 0.0,
        },
        "events": events,
    }
