# sheet_cut

Generates cut-feed programs (step tables → Excel) for cutting transformer core
laminations — side-limb yokes, central limbs, and "fishy fish" patterns — on a
CNC shearing line. The operator transfers the generated `.xlsx` to the machine.

One backend, three client types: a **web app**, the **HTTP API** (OpenAPI),
and an **MCP server** so AI assistants can drive the same workflows.

## Status

The 2021 Tkinter prototype is frozen under [`legacy/`](legacy/README.md) as the
parity oracle; the production system was built per
[`docs/PRODUCTION_PLAN.md`](docs/PRODUCTION_PLAN.md):

| Phase | Scope | State |
|---|---|---|
| 0 | Scaffolding, freeze prototype as parity oracle | ✅ |
| 1 | Algorithms ported to `src/sheetcut/core/` | ✅ 21 golden cases, cell-for-cell parity |
| 2 | Service layer + SQLite persistence | ✅ |
| 3 | HTTP API (FastAPI) | ✅ |
| 4a | MCP server | ✅ |
| 4b | React SPA | ✅ |
| 5 | Hardening | ✅ — `legacy/` is archived only after a production bake period |

Supported pattern types: 1 (side-limb yoke), 3 (spear/central limb),
4 (symmetric fish), 5 (asymmetric fish). Split yoke (2) was broken in the
prototype and is intentionally rejected.

## Deploy on the LAN

```sh
docker compose up -d --build
# open http://<machine>:8000        (SPA + API on one port)
```

All state (SQLite DB + generated `.xlsx`) lives in the `sheetcut-data` volume —
**backup = copy that volume** (e.g. `docker run --rm -v sheetcut-data:/data -v
$PWD:/backup alpine tar czf /backup/sheetcut-backup.tgz /data`).

Optional shared-key auth: set `SHEETCUT_API_KEY` in `docker-compose.yml`;
clients must then send `X-API-Key`. `/api/v1/healthz` stays open.

## HTTP API

Interactive docs at `http://<machine>:8000/docs`. Core endpoints:

```
GET/POST    /api/v1/profiles                profiles (tool sequences)
GET/PUT/DEL /api/v1/profiles/{id}
POST        /api/v1/profiles/{id}/generate  run params -> persisted generation
GET         /api/v1/generations[/{id}]      history, summary, snapshots
GET         /api/v1/generations/{id}/steps  paginated step table
GET         /api/v1/generations/{id}/artifact.xlsx
GET         /api/v1/generations/{id}/plot   series for visualization
GET/PUT     /api/v1/machine-config          versioned calibration (+/history)
```

Every generation snapshots the profile, parameters, and calibration it used,
so what was sent to the machine stays reproducible forever.

## MCP server (AI access)

The MCP server exposes the same services as tools
(`validate_profile`, `create_profile`, `generate_cut_program`,
`get_cut_program_steps`, `get_machine_config`, …). For Claude Desktop/Code:

```json
{
  "mcpServers": {
    "sheetcut": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/sheet_cut", "sheetcut-mcp"],
      "env": { "SHEETCUT_DATA_DIR": "/path/to/sheet_cut/data" }
    }
  }
}
```

Point `SHEETCUT_DATA_DIR` at the same data directory the API uses (or run it
with `SHEETCUT_MCP_TRANSPORT=streamable-http` next to the API container).

## Development

Requires [uv](https://docs.astral.sh/uv/), Python ≥ 3.11, Node 22 (for the SPA).

```sh
uv sync                                   # package + dev tools
uv run pytest                             # 43 tests incl. golden parity
uv run ruff check . && uv run mypy        # lint + strict typing on src/
uv run uvicorn --factory sheetcut.api.main:create_app --reload   # API :8000
cd web && npm install && npm run dev      # SPA dev server :5173 (proxies /api)
```

### Golden-master parity

`legacy/` is frozen — never refactor it. The algorithm ports are pinned by
`tests/golden/data/*.json`, recorded from the legacy code via:

```sh
uv sync --group legacy
uv run python tests/golden/record.py
```

Any intentional behavior change must show up as a reviewed diff in those
golden files. The known-odd legacy behaviors that are deliberately preserved
(fixed iteration caps, the +0.01 duplicate-feed nudge, SpearV's `k*d` fm45
term) are documented in the algorithm module docstrings.

## Layout

```
src/sheetcut/
├── core/         pure domain: models, algorithms, excel/plot export
├── services.py   use-cases shared by all interfaces
├── db.py         SQLAlchemy schema (profiles, generations, config versions)
├── api/          FastAPI app (also serves the built SPA)
└── mcp_server/   MCP tools over the same services
web/              Vite + React + TS SPA (4 screens)
tests/            pytest; tests/golden/ = recorded oracle outputs
legacy/           frozen prototype (parity oracle)
```
