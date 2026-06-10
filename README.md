# sheet_cut

Generates cut-feed programs (step tables → Excel) for cutting transformer core
laminations — side-limb yokes, central limbs, and "fishy fish" patterns — on a
CNC shearing line. The operator transfers the generated `.xlsx` to the machine.

## Status

The original Tkinter prototype is frozen under [`legacy/`](legacy/README.md)
and is being ported into a tested, API-first system (FastAPI backend, React
SPA, MCP server) per [`docs/PRODUCTION_PLAN.md`](docs/PRODUCTION_PLAN.md).

| Phase | Scope | State |
|---|---|---|
| 0 | Scaffolding, freeze prototype as parity oracle | ✅ done |
| 1 | Port algorithms into `src/sheetcut/core/` with golden-master parity tests | not started |
| 2 | Services + SQLite persistence | not started |
| 3 | HTTP API (FastAPI) | not started |
| 4a / 4b | MCP server / React SPA | not started |
| 5 | Hardening, cutover, archive `legacy/` | not started |

## Layout

```
src/sheetcut/   the production package (pure core → services → api/mcp)
tests/          pytest suite; tests/golden/ will hold recorded legacy outputs
legacy/         frozen prototype — the parity oracle; do not refactor
docs/           PRODUCTION_PLAN.md
web/            React SPA (Phase 4b)
```

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.11.

```sh
uv sync               # install package + dev tools (ruff, pytest, mypy)
uv run pytest         # tests
uv run ruff check .   # lint
uv run ruff format .  # format
uv run mypy           # type check (src/ only; legacy/ is excluded)
```

To also install the headless dependencies for driving the legacy oracle
(Phase 1 golden recording): `uv sync --group legacy`.

Running the old GUI is documented in [`legacy/README.md`](legacy/README.md).
