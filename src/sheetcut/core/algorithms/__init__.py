"""Cut-program generation algorithms.

``generate`` dispatches on the profile's pattern type exactly like the legacy
run screen did: type 1 to the side-limb yoke port, types 3/4/5 to the
central-limb/fish port. Type 2 (split yoke) was broken in the prototype and
is intentionally not supported in v1.
"""

from __future__ import annotations

from sheetcut.core.algorithms import central_limb, side_limb_yoke
from sheetcut.core.models import (
    CutProfile,
    CutProgram,
    GenerationError,
    MachineConfig,
    PatternType,
    RunParameters,
)

__all__ = ["generate"]


def generate(profile: CutProfile, params: RunParameters, config: MachineConfig) -> CutProgram:
    ptype = profile.pattern_type
    if ptype == PatternType.SIDE_LIMB_YOKE:
        return side_limb_yoke.generate(profile, params, config)
    if ptype in (
        PatternType.SPEAR_HORIZONTAL,
        PatternType.FISH_SYMMETRIC,
        PatternType.FISH_ASYMMETRIC,
    ):
        return central_limb.generate(profile, params, config)
    raise GenerationError(
        "split-yoke profiles are not supported (the legacy implementation "
        "was non-functional); supported pattern types: 1, 3, 4, 5"
    )
