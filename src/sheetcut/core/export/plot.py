"""Plot-series JSON for client-side visualization.

Derives, from a generated program, the absolute coil position of every cut in
the executable window (Start Index..End Index) so a client can render the
sheet layout (SVG/canvas) without re-implementing any machine math.
"""

from __future__ import annotations

from typing import Any

from sheetcut.core.models import CutProgram


def plot_series(program: CutProgram) -> dict[str, Any]:
    position = 0.0
    events: list[dict[str, Any]] = []
    for i, feed in enumerate(program.feed):
        position = round(position + feed, 5)
        events.append(
            {
                "row": i + 1,
                "tool": program.operation[i] if i < len(program.operation) else None,
                "tool_number": (program.tool_number[i] if i < len(program.tool_number) else None),
                "feed": feed,
                "position": position,
            }
        )
    return {
        "pattern_type": int(program.pattern_type),
        "pattern_length": program.pattern_length,
        "start_index": program.start_index[0] if program.start_index else None,
        "end_index": program.end_index[0] if program.end_index else None,
        "sheet_count": program.sheet_count[0] if program.sheet_count else None,
        "v_axis": list(program.v_axis),
        "events": events,
    }
