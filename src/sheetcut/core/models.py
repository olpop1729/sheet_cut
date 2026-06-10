"""Pure domain models for cut-program generation.

These formalize the ad-hoc dicts/JSON of the legacy prototype:

- profile JSON written by the legacy GUI (``legacy/gui/create_cut_program.py``):
  ``{"0": {"name": "fp45", "steplap_type": 1, "steplap_count": 5,
  "open_code": 1, "is_skewed": false, "_steplap_distance": 0}, ...}``
- run parameter JSON (``legacy/data/*.json`` on the neo branch)
- machine calibration (``legacy/gui/config.json`` + ``shared.config.Config``)
- the 15-column Excel step table written by ``shared.pandas_utils``.
"""

from __future__ import annotations

import itertools
from enum import IntEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator

# Tool name strings as used by the machine programs. Kept as plain strings in
# specs (the legacy tool set includes partial-cut names we don't generate for)
# with the well-known ones as constants.
TOOL_HOLE = "h"
TOOL_VNOTCH = "v"
TOOL_FP45 = "fp45"
TOOL_FM45 = "fm45"
TOOL_F0 = "f0"
TOOL_SPEAR = "s"
TOOL_YOKE_SPLITTER = "ys"

KNOWN_TOOLS = (
    TOOL_FM45,
    TOOL_FP45,
    TOOL_F0,
    TOOL_VNOTCH,
    TOOL_HOLE,
    TOOL_SPEAR,
    TOOL_YOKE_SPLITTER,
)

FULL_CUTS = (TOOL_FP45, TOOL_FM45, TOOL_F0)

# Machine tool numbers (legacy: last element of Config.TOOL_NAME_MAP entries).
TOOL_NUMBER = {
    TOOL_HOLE: 2,
    TOOL_VNOTCH: 1,
    TOOL_FM45: 5,
    TOOL_FP45: 4,
    TOOL_F0: 3,
}

# Excel column headers, byte-for-byte the legacy order.
EXCEL_COLUMN_NAMES = [
    "Feed Dist",
    "Vnotch Trav Dist",
    "After Shear feed Tip Cut",
    "Tool",
    "Tool no",
    "Start Index",
    "End Index",
    "Job Shape",
    "No of Steps",
    "Sheet Count",
    "P45 OverCut",
    "M45 OverCut",
    "Yoke Len",
    "Leg Len",
    "Central Limb Len",
]


class StepLapType(IntEnum):
    """Legacy ``Labels.steplap_type_map`` values."""

    NONE = 0
    HORIZONTAL = 1  # longitudinal
    VERTICAL = 2  # lateral
    SKEWED = 3  # lateral, skewed


class OpenCode(IntEnum):
    """Legacy ``Labels.open_code_map`` values."""

    NA = 0
    OPEN = 1
    CLOSED = 2
    FRONT_OPEN_REAR_OPEN = 3
    FRONT_OPEN_REAR_CLOSED = 4
    FRONT_CLOSED_REAR_OPEN = 5
    FRONT_CLOSED_REAR_CLOSED = 6
    FRONT_OPEN = 7
    FRONT_CLOSED = 8
    REAR_OPEN = 9
    REAR_CLOSED = 10


class PatternType(IntEnum):
    """Legacy ``RunScreen._ptype`` values."""

    SIDE_LIMB_YOKE = 1
    SPLIT_YOKE = 2
    SPEAR_HORIZONTAL = 3
    FISH_SYMMETRIC = 4
    FISH_ASYMMETRIC = 5


class ToolSpec(BaseModel):
    """One row of a cut profile (one tool in the sequence)."""

    name: str
    steplap_type: int = StepLapType.NONE
    steplap_count: int = 1
    open_code: int = OpenCode.NA
    is_skewed: bool = False

    @field_validator("name")
    @classmethod
    def _name_known(cls, v: str) -> str:
        if v not in KNOWN_TOOLS:
            raise ValueError(f"unknown tool name {v!r}; expected one of {KNOWN_TOOLS}")
        return v

    @field_validator("steplap_count")
    @classmethod
    def _count_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("steplap_count must be >= 1")
        return v


class CutProfile(BaseModel):
    """An ordered tool sequence defining a cut pattern."""

    name: str = ""
    tools: list[ToolSpec] = Field(min_length=1)

    @property
    def pattern_type(self) -> PatternType:
        """Port of the ptype inference in ``legacy/gui/run_screen.py``."""
        for tool in self.tools:
            if tool.name == TOOL_SPEAR:
                if tool.steplap_type == StepLapType.VERTICAL:
                    return (
                        PatternType.FISH_ASYMMETRIC
                        if tool.is_skewed
                        else PatternType.FISH_SYMMETRIC
                    )
                if tool.steplap_type == StepLapType.SKEWED:
                    return PatternType.FISH_ASYMMETRIC
                return PatternType.SPEAR_HORIZONTAL
            if tool.name == TOOL_YOKE_SPLITTER:
                return PatternType.SPLIT_YOKE
        return PatternType.SIDE_LIMB_YOKE

    @property
    def steplap_tool_count(self) -> int:
        """Number of tools that need a step-lap distance at run time."""
        return sum(1 for t in self.tools if t.steplap_count > 1)

    @classmethod
    def from_legacy_data(cls, data: dict[str, Any], name: str = "") -> CutProfile:
        """Build from the GUI's profile JSON (``{"0": {...}, "1": {...}}``)."""
        tools = []
        for _, raw in sorted(data.items(), key=lambda kv: int(kv[0])):
            tools.append(
                ToolSpec(
                    name=raw["name"],
                    steplap_type=raw.get("steplap_type", 0),
                    steplap_count=max(int(raw.get("steplap_count", 1)), 1),
                    open_code=raw.get("open_code", 0),
                    is_skewed=raw.get("is_skewed", False),
                )
            )
        return cls(name=name, tools=tools)

    def to_legacy_data(self) -> dict[str, Any]:
        """Render the GUI-compatible profile dict (used by golden tests)."""
        return {
            str(i): {
                "name": t.name,
                "steplap_type": t.steplap_type,
                "steplap_count": t.steplap_count,
                "open_code": t.open_code,
                "is_skewed": t.is_skewed,
                "_steplap_distance": 0,
            }
            for i, t in enumerate(self.tools)
        }


class RunParameters(BaseModel):
    """Per-run inputs the operator enters on the run screen."""

    length_list: list[float] = Field(min_length=1)
    steplap_distances: list[float] = Field(default_factory=list)
    layers: int = Field(default=1, ge=1)
    start_sheet: int = Field(default=1, ge=1)
    scrap_length: float = Field(default=0.0, ge=0.0)


class MachineConfig(BaseModel):
    """Machine calibration; values mirror ``legacy/gui/config.json``."""

    offset_fp45: float = 0.75
    offset_fm45: float = 0.865
    offset_f0: float = 0.0
    offset_v_lat: float = 0.5
    distance_hole_vnotch: float = 1250.0
    distance_shear_vnotch: float = 4334.5
    coil_length: float = 400000.0

    def shear_offset(self, tool: str) -> float:
        return {
            TOOL_FP45: self.offset_fp45,
            TOOL_FM45: self.offset_fm45,
            TOOL_F0: self.offset_f0,
        }[tool]


class CutProgram(BaseModel):
    """The generated step table — the 15 legacy Excel columns plus metadata.

    Columns intentionally have different lengths, exactly as the legacy
    writer received them (it pads with blanks via ``zip_longest``).
    """

    feed: list[float] = Field(default_factory=list)
    v_axis: list[float] = Field(default_factory=list)
    sec_feed: list[float] = Field(default_factory=list)
    operation: list[str] = Field(default_factory=list)
    tool_number: list[int] = Field(default_factory=list)
    start_index: list[int] = Field(default_factory=list)
    end_index: list[int] = Field(default_factory=list)
    job_shape: list[float] = Field(default_factory=list)
    number_of_steps: list[int] = Field(default_factory=list)
    sheet_count: list[int] = Field(default_factory=list)
    p45_overcut: list[float] = Field(default_factory=list)
    m45_overcut: list[float] = Field(default_factory=list)
    yoke_len: list[float] = Field(default_factory=list)
    leg_len: list[float] = Field(default_factory=list)
    cl_len: list[float] = Field(default_factory=list)

    # Metadata (not part of the Excel artifact)
    pattern_type: PatternType
    pattern_length: float | None = None
    warnings: list[str] = Field(default_factory=list)

    def columns(self) -> list[tuple[str, list[Any]]]:
        """The 15 columns in legacy Excel order."""
        return [
            (EXCEL_COLUMN_NAMES[0], list(self.feed)),
            (EXCEL_COLUMN_NAMES[1], list(self.v_axis)),
            (EXCEL_COLUMN_NAMES[2], list(self.sec_feed)),
            (EXCEL_COLUMN_NAMES[3], list(self.operation)),
            (EXCEL_COLUMN_NAMES[4], list(self.tool_number)),
            (EXCEL_COLUMN_NAMES[5], list(self.start_index)),
            (EXCEL_COLUMN_NAMES[6], list(self.end_index)),
            (EXCEL_COLUMN_NAMES[7], list(self.job_shape)),
            (EXCEL_COLUMN_NAMES[8], list(self.number_of_steps)),
            (EXCEL_COLUMN_NAMES[9], list(self.sheet_count)),
            (EXCEL_COLUMN_NAMES[10], list(self.p45_overcut)),
            (EXCEL_COLUMN_NAMES[11], list(self.m45_overcut)),
            (EXCEL_COLUMN_NAMES[12], list(self.yoke_len)),
            (EXCEL_COLUMN_NAMES[13], list(self.leg_len)),
            (EXCEL_COLUMN_NAMES[14], list(self.cl_len)),
        ]

    def rows(self) -> list[list[Any]]:
        """Row-major view padded with ``None``, as the Excel sheet lays out."""
        cols = [values for _, values in self.columns()]
        return [list(row) for row in itertools.zip_longest(*cols)]

    @property
    def row_count(self) -> int:
        return max((len(values) for _, values in self.columns()), default=0)


class GenerationError(ValueError):
    """Raised when a profile/parameter combination cannot be generated."""
