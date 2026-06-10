"""Central-limb and fish patterns — faithful port of ``legacy/gui/central_limb_v2.py``.

``TooList_CL`` dispatches on pattern type: SpearH (type 3, horizontal step-lap
spear) and SpearV (types 4/5, symmetric/asymmetric "fishy fish"). Arithmetic
order and ``round(x, 5)`` placement are preserved bit-for-bit.

Deliberately preserved legacy behaviors (do not "fix" without a golden diff):

- only ``tools[0]``'s steplap_count/open_code are read, like the original
- the execution loop runs fixed iterations (500 fish / 200 spear-H) and the
  full untrimmed table is written; Start/End Index columns mark the window
- ``sum(2 * dn[:i])`` keeps the legacy list-concatenation summation order
- SpearV's fm45 position uses ``(l + k*d) * i`` while fp45/v use
  ``(l + (n-1)*d)`` terms — asymmetric on purpose until the owner rules on it
- Sheet Count is left empty for these patterns (legacy passes ``[]``)
"""

from __future__ import annotations

from dataclasses import dataclass

from sheetcut.core.models import (
    TOOL_NUMBER,
    CutProfile,
    CutProgram,
    GenerationError,
    MachineConfig,
    PatternType,
    RunParameters,
)


@dataclass
class _Cut:
    """One scheduled cut: tool name, coil position, lateral value (spear-H)."""

    name: str
    pos: float
    lat: float = 0.0


def generate(profile: CutProfile, params: RunParameters, config: MachineConfig) -> CutProgram:
    """Port of ``TooList_CL.__init__`` + ``_ptype_decider``."""
    ptype = profile.pattern_type
    first = profile.tools[0]

    steplap_distance = 0.0
    if params.steplap_distances:
        steplap_distance = params.steplap_distances[0]

    if ptype == PatternType.SPEAR_HORIZONTAL:
        return _spear_h(
            steplap_distance=steplap_distance,
            scrap_length=params.scrap_length,
            len_list=list(params.length_list),
            steplap_count=first.steplap_count,
            open_code=first.open_code,
            layers=params.layers,
            config=config,
        )
    if ptype in (PatternType.FISH_SYMMETRIC, PatternType.FISH_ASYMMETRIC):
        return _spear_v(
            steplap_distance=steplap_distance,
            len_list=list(params.length_list),
            steplap_count=first.steplap_count,
            layers=params.layers,
            ptype=ptype,
            config=config,
        )
    raise GenerationError(f"central_limb cannot generate pattern type {ptype}")


def _spear_v(
    *,
    steplap_distance: float,
    len_list: list[float],
    steplap_count: int,
    layers: int,
    ptype: PatternType,
    config: MachineConfig,
) -> CutProgram:
    """Port of ``SpearV`` (fishy fish)."""
    d = steplap_distance
    n = steplap_count
    m = layers

    # create_hole_list
    pos = 0.0
    hole: list[float] = []
    if len(len_list) > 1:
        for i in range(len(len_list) - 1):
            pos = pos + len_list[i]
            hole.append(pos)

    k = n // 2 if ptype == PatternType.FISH_SYMMETRIC else n - 1

    fish_len = sum(len_list)
    l = fish_len  # noqa: E741 - mirrors the legacy variable names
    mult = 1

    # create_dict
    exe: list[_Cut] = []
    for i in range(n * m):
        if len(hole) > 0:
            for j in hole:
                exe.append(_Cut("h", i * (l + mult * (n - 1) * d) + j + (2 * k - i // m) * d))
        exe.append(_Cut("fm45", (3 * k - 2 * (i // m)) * d + (l + mult * k * d) * i))
        exe.append(_Cut("fp45", (k - 2 * (i // m)) * d + ((l + mult * (n - 1) * d) * (i + 1))))
        exe.append(_Cut("v", i * (fish_len + mult * (n - 1) * d)))
    pattern_length = round(n * (l + mult * (n - 1) * d) * m, 5)

    # execute
    for cut in exe:
        if cut.name == "fp45":
            cut.pos += config.distance_shear_vnotch + config.offset_fp45
        elif cut.name == "fm45":
            cut.pos += config.distance_shear_vnotch + config.offset_fm45
        elif cut.name == "h":
            cut.pos += config.distance_hole_vnotch
        cut.pos = round(cut.pos, 5)

    terminate = 500
    feed: list[float] = []
    vaxis: list[float] = []
    operation: list[str] = []
    tool_number: list[int] = []

    while terminate > 0:
        terminate -= 1
        close = min(cut.pos for cut in exe)
        repeat = False
        for cut in exe:
            if cut.pos == close:
                if cut.name == "v":
                    vaxis.append(k * d)
                else:
                    vaxis.append(0)
                if repeat:
                    feed.append(0)
                else:
                    feed.append(close)
                operation.append(cut.name)
                tool_number.append(TOOL_NUMBER[cut.name])
                cut.pos = pattern_length
                repeat = True
            else:
                cut.pos -= close
                cut.pos = round(cut.pos, 5)

    start_index = 0
    for i in range(len(operation)):
        if operation[i][0] == "f":
            start_index = i
            break
    start_index += 2
    end_index = start_index + len(exe) - 1

    return CutProgram(
        feed=feed,
        v_axis=vaxis,
        operation=operation,
        tool_number=tool_number,
        start_index=[start_index],
        end_index=[end_index],
        pattern_type=ptype,
        pattern_length=pattern_length,
    )


def _spear_h(
    *,
    steplap_distance: float,
    scrap_length: float,
    len_list: list[float],
    steplap_count: int,
    open_code: int,
    layers: int,
    config: MachineConfig,
) -> CutProgram:
    """Port of ``SpearH`` (central limb, horizontal step-lap)."""
    if layers > 1 and len(len_list) > 1:
        raise GenerationError(
            "the legacy spear-horizontal algorithm only supports layers=1 "
            "when the profile has hole positions (it indexed past the "
            "step-lap vector otherwise); split the run into single layers"
        )

    d = steplap_distance
    x = scrap_length

    # gen_hole_list
    hole_list = [sum(len_list[: i + 1]) for i in range(len(len_list) - 1)]

    # gen_steplap_vector
    half = steplap_count // 2
    if steplap_count % 2 == 0:
        dn = [round((i - i / (2 * abs(i))) * d, 5) for i in range(half, -half - 1, -1) if i != 0]
    else:
        dn = [i * d for i in range(half, -half - 1, -1)]
    if open_code == 2:
        dn = dn[::-1]

    # create_dict
    n = steplap_count
    m = layers
    l = sum(len_list)  # noqa: E741 - mirrors the legacy variable names
    exe: list[_Cut] = []
    for i in range(n * m):
        vtv = sum(2 * dn[:i]) + i * (l + 2 * x)
        vtv = round(vtv, 5)
        if len(hole_list) > 0:
            for j in hole_list:
                exe.append(_Cut("h", round(vtv + j + x + dn[i], 5), 0))
        exe.append(_Cut("v", vtv, x))
        exe.append(_Cut("fp45", round(vtv - x, 5), 0))
        exe.append(_Cut("fm45", round(vtv + x, 5), 0))
    pl = round((l + 2 * x) * m * n, 5)

    # execute
    for cut in exe:
        if cut.name == "fm45":
            cut.pos += config.distance_shear_vnotch + config.offset_fm45
        elif cut.name == "fp45":
            cut.pos += config.distance_shear_vnotch + config.offset_fp45
        elif cut.name == "h":
            cut.pos += config.distance_hole_vnotch
        cut.pos = round(cut.pos, 5)

    term = 200
    feed: list[float] = []
    operation: list[str] = []
    vaxis: list[float] = []
    tool_number: list[int] = []

    while term > 0:
        term -= 1
        cc = min(cut.pos for cut in exe)
        repeat = False
        for cut in exe:
            if cut.pos == cc:
                vaxis.append(cut.lat)
                operation.append(cut.name)
                tool_number.append(TOOL_NUMBER[cut.name])
                if repeat:
                    feed.append(0)
                else:
                    feed.append(cc)
                    repeat = True
                cut.pos = pl
            else:
                cut.pos -= cc
                cut.pos = round(cut.pos, 5)

    start_index = 0
    for i in range(len(operation)):
        if operation[i][0] == "f":
            start_index = i
            break
    start_index += 2
    end_index = start_index + len(exe) - 1

    return CutProgram(
        feed=feed,
        v_axis=vaxis,
        operation=operation,
        tool_number=tool_number,
        start_index=[start_index],
        end_index=[end_index],
        pattern_type=PatternType.SPEAR_HORIZONTAL,
        pattern_length=pl,
    )
