"""Golden-master parity: sheetcut.core must reproduce the legacy prototype
cell-for-cell on the recorded matrix (tests/golden/data/, produced by
tests/golden/record.py from the frozen code in legacy/)."""

import json
import math
from pathlib import Path

import pytest

from sheetcut.core import CutProfile, MachineConfig, RunParameters, generate
from sheetcut.core.export.excel import read_grid, write_xlsx

GOLDEN_DIR = Path(__file__).parent / "golden" / "data"
GOLDEN_FILES = sorted(GOLDEN_DIR.glob("*.json"))


def _params(case: dict) -> RunParameters:
    return RunParameters(
        length_list=case["l_list"],
        steplap_distances=case["d_list"],
        layers=case["layers"],
        start_sheet=case["s_no"],
        scrap_length=case["scrap_length"],
    )


@pytest.mark.parametrize("golden_path", GOLDEN_FILES, ids=lambda p: p.stem)
def test_parity(golden_path: Path) -> None:
    doc = json.loads(golden_path.read_text())
    case = doc["case"]

    profile = CutProfile.from_legacy_data(case["profile"], name=case["id"])
    assert profile.pattern_type == case["ptype"], "pattern-type inference diverged"

    program = generate(profile, _params(case), MachineConfig(**doc["machine_config"]))
    ours = read_grid(write_xlsx(program))
    golden = doc["grid"]

    assert len(ours) == len(golden), f"row count: ours={len(ours)} golden={len(golden)}"
    for r, (mine, gold) in enumerate(zip(ours, golden, strict=True)):
        assert len(mine) == len(gold), f"row {r}: width {len(mine)} != {len(gold)}"
        for c, (a, b) in enumerate(zip(mine, gold, strict=True)):
            if (
                isinstance(a, int | float)
                and isinstance(b, int | float)
                and not isinstance(a, bool)
                and not isinstance(b, bool)
            ):
                assert math.isclose(a, b, rel_tol=0.0, abs_tol=1e-9), (
                    f"cell ({r},{c}): ours={a!r} golden={b!r}"
                )
            else:
                assert a == b, f"cell ({r},{c}): ours={a!r} golden={b!r}"


def test_golden_corpus_present() -> None:
    assert len(GOLDEN_FILES) >= 21, "golden corpus missing; run tests/golden/record.py"
