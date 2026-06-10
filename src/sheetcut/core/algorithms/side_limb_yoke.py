"""Side-limb yoke generation — faithful port of ``legacy/step_lap/step_lap_v4.py``.

The legacy ``ToolList`` class is the oracle (it is what the Tkinter GUI runs
for pattern type 1). This port preserves its arithmetic order and every
``round(x, 5)`` call so outputs are bit-identical; only I/O (prints, Excel
writing, ``sys.exit``) is removed and input errors raise ``GenerationError``.

Deliberately preserved legacy behaviors (do not "fix" without a golden diff):

- the execution loop runs a fixed 200 iterations and is trimmed afterwards
- consecutive duplicate feed values are nudged by +0.01 (``_feed_post``)
- ``v_axis`` is truncated to one entry per step-lap level
- float equality is used to match cut positions; it holds because both sides
  of every comparison go through identical accumulate-then-round paths
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sheetcut.core.models import (
    FULL_CUTS,
    TOOL_NUMBER,
    TOOL_SPEAR,
    CutProfile,
    CutProgram,
    GenerationError,
    MachineConfig,
    PatternType,
    RunParameters,
)


@dataclass
class _Tool:
    """Port of ``step_lap_v4.Tool`` (state machine over the step-lap vector)."""

    name: str
    steplap_count: int
    steplap_type: int
    open_code: int
    steplap_distance: float = 0.0
    steplap_vector: list[float] = field(default_factory=list)
    front_counter: int = 0
    rear_counter: int = 0

    def generate_steplap_vector(self) -> None:
        d = self.steplap_distance
        n = self.steplap_count
        if n > 1:
            if n % 2 == 0:
                self.steplap_vector = [
                    (i - i / (2 * abs(i))) * d for i in range(n // 2, -n // 2 - 1, -1) if i != 0
                ]
            else:
                self.steplap_vector = [i * d for i in range(n // 2, -n // 2, -1)]

    def set_steplap_counter(self) -> None:
        if self.open_code in [4, 1, 7, 10]:
            self.front_counter = 0
            self.rear_counter = self.steplap_count - 1
        elif self.open_code in [2, 5, 8, 9]:
            self.front_counter = self.steplap_count - 1
            self.rear_counter = 0
        elif self.open_code == 3:
            self.front_counter = 0
            self.rear_counter = 0
        elif self.open_code == 6:
            self.front_counter = self.steplap_count - 1
            self.rear_counter = self.steplap_count - 1

    def increment_steplap_counter(self) -> None:
        f = self.front_counter
        r = self.rear_counter
        n = self.steplap_count
        if self.open_code in (1, 4):
            f = (f + 1) % n
            r = (r - 1) % n
        elif self.open_code in (2, 5):
            f = (f - 1) % n
            r = (r + 1) % n
        elif self.open_code == 3:
            f = (f + 1) % n
            r = (r + 1) % n
        elif self.open_code == 6:
            f = (f - 1) % n
            r = (r - 1) % n
        self.front_counter = f
        self.rear_counter = r


@dataclass
class _ETool:
    """Port of ``circuit.eTool`` (an executable cut at a coil position)."""

    name: str
    long: float
    lat: float


def generate(profile: CutProfile, params: RunParameters, config: MachineConfig) -> CutProgram:
    tools = [
        _Tool(
            name=t.name,
            steplap_count=t.steplap_count,
            steplap_type=t.steplap_type,
            open_code=t.open_code,
        )
        for t in profile.tools
    ]
    lengths = list(params.length_list)

    if len(lengths) != len(tools) - 1:
        raise GenerationError(
            f"side-limb yoke needs len(tools) - 1 lengths: "
            f"{len(tools)} tools require {len(tools) - 1}, got {len(lengths)}"
        )
    needed = sum(1 for t in tools if t.steplap_count > 1)
    if len(params.steplap_distances) < needed:
        raise GenerationError(
            f"profile has {needed} step-lap tools but only "
            f"{len(params.steplap_distances)} step-lap distances were given"
        )

    # _populate_data: distances are assigned to steplap tools in tool order.
    d_counter = 0
    for tool in tools:
        if tool.steplap_count > 1:
            tool.steplap_distance = params.steplap_distances[d_counter]
            d_counter += 1

    # _ready_steplaps
    stepcount = max(t.steplap_count for t in tools)
    if not stepcount:
        stepcount = 1
    for tool in tools:
        tool.generate_steplap_vector()
        tool.set_steplap_counter()

    nl_total = _lengthyfy(tools, lengths, stepcount, params.layers)
    etools, sheet_count, pattern_length = _map_exe(tools, nl_total, params.start_sheet, config)
    return _exe(
        etools,
        nl_total,
        sheet_count,
        pattern_length,
        stepcount,
        config,
    )


def _lengthyfy(
    tools: list[_Tool], lengths: list[float], stepcount: int, layers: int
) -> list[list[float]]:
    """Port of ``ToolList._lengthyfy``: token lengths per step-lap level."""
    fnl: list[list[float]] = []
    for _ in range(stepcount):
        nl: list[list[float]] = []
        for i in range(len(lengths)):
            tool = tools[i]
            try:
                if tool.steplap_type == 0:
                    nl.append([lengths[i], 0])
                elif tool.steplap_type == 1:
                    if tool.name in ("h", "v"):
                        if tool.open_code in [1, 2]:
                            nl[-1][0] += tool.steplap_vector[tool.rear_counter]
                            nl.append([lengths[i] + tool.steplap_vector[tool.front_counter], 0])
                            tool.increment_steplap_counter()
                        elif tool.open_code in [3, 4, 5, 6]:
                            pass
                    elif tool.name in FULL_CUTS:
                        if tool.open_code in [1, 2, 7, 8]:
                            nl.append([lengths[i] + tool.steplap_vector[tool.front_counter], 0])
                            tool.increment_steplap_counter()
                        elif tool.open_code in [3, 4, 5, 6]:
                            nl[-1][0] += tool.steplap_vector[tool.rear_counter]
                            nl.append([lengths[i] + tool.steplap_vector[tool.front_counter], 0])
                            tool.increment_steplap_counter()
                        elif tool.open_code in [9, 10]:
                            nl[-1][0] += tool.steplap_vector[tool.rear_counter]
                            tool.increment_steplap_counter()
                elif tool.steplap_type == 2 and tool.name == "v" and tool.open_code in [1, 2]:
                    nl.append([lengths[i], tool.steplap_vector[tool.rear_counter]])
                    tool.increment_steplap_counter()

                if i == len(lengths) - 1:
                    last = tools[i + 1]
                    if (
                        last.steplap_type == 1
                        and last.name in FULL_CUTS
                        and last.open_code in [1, 2]
                    ):
                        nl[-1][0] += last.steplap_vector[last.front_counter]
                        last.increment_steplap_counter()
            except IndexError as err:
                raise GenerationError(
                    f"profile is not a valid side-limb yoke sequence at tool "
                    f"{i + 1} ({tool.name!r}): {err}"
                ) from err

        for _layer in range(layers):
            fnl.extend([row[0], row[1]] for row in nl)
    return fnl


def _map_exe(
    tools: list[_Tool],
    nl_total: list[list[float]],
    start_sheet: int,
    config: MachineConfig,
) -> tuple[list[_ETool], int, float]:
    """Port of ``ToolList._map_exe``: logical tokens -> physical positions."""
    modulo = len(tools) - 1
    long = 0.0
    sc = 0
    inner: list[_ETool] = []

    for i in range(len(nl_total)):
        tool = tools[i % modulo]
        if tool.name == "h":
            inner.append(_ETool("h", long, 0))
        elif tool.name == "v":
            inner.append(_ETool("v", long, nl_total[i][1]))
        elif tool.name in FULL_CUTS:
            sc += 1
            inner.append(_ETool(tool.name, long, 0))
        elif tool.name == TOOL_SPEAR:
            sc += 1
        long += nl_total[i][0]
        long = round(long, 5)

    long = float(round(long, 5))
    if sc == 0:
        raise GenerationError("profile produces no sheet-separating cuts")

    rotation_pt = (start_sheet - 1) % sc

    temp = 0
    rot = 0.0
    for etool in inner:
        if etool.name[0] == "f":
            if temp == rotation_pt:
                rot = etool.long
                break
            temp += 1

    for etool in inner:
        etool.long -= rot
        if etool.long < 0:
            etool.long += long

    for etool in inner:
        if etool.name in FULL_CUTS:
            etool.long += config.distance_shear_vnotch + config.shear_offset(etool.name)
        elif etool.name == "h":
            etool.long += config.distance_hole_vnotch
        etool.long = round(etool.long, 5)

    return inner, sc, long


def _exe(
    etools: list[_ETool],
    nl_total: list[list[float]],
    sheet_count: int,
    pattern_length: float,
    stepcount: int,
    config: MachineConfig,
) -> CutProgram:
    """Port of ``ToolList._exe``: simulate the coil run and trim the table."""
    terminate = 200
    operation: list[str] = []
    tool_number: list[int] = []
    feed: list[float] = []
    v_axis: list[float] = []
    repeat_flag = False

    while terminate > 0:
        closest_cut = min(e.long for e in etools)
        for e in etools:
            if e.long == closest_cut:
                e.long = pattern_length
                if repeat_flag:
                    feed.append(0)
                else:
                    feed.append(closest_cut)
                    repeat_flag = True
                if e.name == "v":
                    v_axis.append(e.lat)
                operation.append(e.name)
                tool_number.append(TOOL_NUMBER[e.name])
            else:
                e.long -= closest_cut
                e.long = round(e.long, 5)
        repeat_flag = False
        terminate -= 1

    start_index = 0
    for i in range(len(operation)):
        if operation[i][0] == "f":
            start_index = i
            break
    start_index += 2
    end_index = start_index + len(nl_total) - 1

    feed = _feed_post(feed[:end_index])
    operation = operation[:end_index]
    v_axis = v_axis[:stepcount]
    tool_number = tool_number[:end_index]

    return CutProgram(
        feed=feed,
        v_axis=v_axis,
        operation=operation,
        tool_number=tool_number,
        start_index=[start_index],
        end_index=[end_index],
        sheet_count=[sheet_count],
        pattern_type=PatternType.SIDE_LIMB_YOKE,
        pattern_length=pattern_length,
    )


def _feed_post(values: list[float]) -> list[float]:
    """Legacy duplicate-feed nudge, including its quirk of comparing against
    the already-nudged previous value."""
    prev = None
    for i in range(len(values)):
        if values[i] == prev:
            values[i] += 0.01
        prev = values[i]
    return values
