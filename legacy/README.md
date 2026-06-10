# legacy/ — frozen prototype (the parity oracle)

This is the original 2021–2025 prototype, moved here unchanged in Phase 0 of
[the production plan](../docs/PRODUCTION_PLAN.md). It is the **golden-master
oracle** for the port into `src/sheetcut/core/` — do not refactor or "improve"
code in this directory. Behavior changes happen only in `src/sheetcut/`, as
explicit diffs against recorded golden outputs.

Layout (paths are relative to this directory, exactly as they were at the repo
root):

- `step_lap/` — algorithm scripts; `step_lap_v4.py` is what the GUI runs
- `gui/` — Tkinter app (`tkinter_v1.py` is the entry point) + `central_limb_v2.py`
- `shared/` — common tool classes/config extracted by PR #1
- `cut_program_input/`, `cut_program_output/` — profile JSONs and generated Excel
- `no_step_lap/`, `pretty_input_program/`, `sql/`, `screenshots/` — older experiments

To run the old GUI (needs a display): from this directory,
`python gui/tkinter_v1.py` with `pandas`, `numpy`, `matplotlib`, `plotly`,
`openpyxl` installed (the `legacy` dependency group in the root `pyproject.toml`
covers the headless subset used for golden recording).

This directory is excluded from ruff/mypy and will be archived once parity is
proven and the cutover completes (Phase 5).
