"""Golden-master recorder: drive the frozen legacy code, snapshot its Excel output.

Run from the repo root with the legacy dependency group installed:

    uv sync --group legacy
    uv run python tests/golden/record.py

For each case in ``cases.py`` this instantiates the legacy ``ToolList`` /
``TooList_CL`` (which generate and write an .xlsx as a side effect), reads
the resulting sheet back, and stores inputs + machine config + cell grid as
``tests/golden/data/<id>.json``. Re-run only when intentionally re-baselining;
the resulting diff is the review artifact.
"""

# ruff: noqa: E402, I001 - imports must happen after the chdir below

import contextlib
import io
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEGACY = REPO / "legacy"
DATA_DIR = Path(__file__).resolve().parent / "data"

sys.path.insert(0, str(LEGACY / "gui"))
sys.path.insert(0, str(LEGACY / "step_lap"))
sys.path.insert(0, str(REPO / "src"))

# The legacy modules read ../gui/config.json and write ../cut_program_output/
# relative to the CWD, and instantiate Config() at import time — so chdir
# before importing them.
os.chdir(LEGACY / "step_lap")

from central_limb_v2 import TooList_CL, conf as cl_conf
from step_lap_v4 import ToolList

from sheetcut.core.export.excel import read_grid

from cases import CASES

OUTPUT_DIR = LEGACY / "cut_program_output"


def machine_config() -> dict:
    cfg = {
        "offset_fp45": cl_conf.OFFSET_FP45,
        "offset_fm45": cl_conf.OFFSET_FM45,
        "offset_f0": cl_conf.OFFSET_F0,
        "offset_v_lat": cl_conf.OFFSET_V_LAT,
        "distance_hole_vnotch": cl_conf.DISTANCE_HOLE_VNOTCH,
        "distance_shear_vnotch": cl_conf.DISTANCE_SHEAR_VNOTCH,
        "coil_length": cl_conf.COIL_LENGTH,
    }
    # Guard against silently falling back to class defaults (wrong CWD would
    # load no JSON and record an unintended baseline).
    assert cfg["distance_shear_vnotch"] == 4334.5, (
        "legacy gui/config.json was not loaded; refusing to record"
    )
    assert cfg["offset_fp45"] == 0.75, "unexpected OFFSET_FP45; config not loaded?"
    return cfg


def run_case(case: dict) -> Path:
    fname = f"golden_{case['id']}"
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        if case["ptype"] == 1:
            ToolList(
                data=case["profile"],
                d_list=list(case["d_list"]),
                l_list=list(case["l_list"]),
                f_name=fname,
                s_no=case["s_no"],
                layers=case["layers"],
            )
        else:
            TooList_CL(
                data=case["profile"],
                d_list=list(case["d_list"]),
                l_list=list(case["l_list"]),
                f_name=fname,
                s_no=case["s_no"],
                scrap_length=case["scrap_length"],
                p_type=case["ptype"],
                layers=case["layers"],
            )
    return OUTPUT_DIR / f"{fname}.xlsx"


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cfg = machine_config()
    failures = []
    for case in CASES:
        xlsx = run_case(case)
        if not xlsx.exists():
            failures.append((case["id"], "no xlsx produced"))
            continue
        grid = read_grid(str(xlsx))
        out = DATA_DIR / f"{case['id']}.json"
        with open(out, "w") as fp:
            json.dump(
                {"case": case, "machine_config": cfg, "grid": grid},
                fp,
                indent=1,
            )
        print(f"recorded {case['id']:28s} rows={len(grid) - 1}")
        xlsx.unlink()  # keep the legacy output dir clean
    if failures:
        for cid, why in failures:
            print(f"FAILED {cid}: {why}")
        return 1
    print(f"\n{len(CASES)} golden files in {DATA_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
