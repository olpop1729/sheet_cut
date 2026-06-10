# sheet_cut — Production Architecture Plan

Target: turn the 2021 Tkinter prototype into a structured, tested, deployable system
with one backend serving three client types: **web app**, **mobile (later)**, and **MCP**
(Model Context Protocol, for AI/agent access).

Decisions locked in:

| Decision | Choice |
|---|---|
| Deployment | LAN-first (Docker on a factory/office PC), designed cloud-ready |
| Web frontend | React SPA (Vite + TypeScript) |
| v1 algorithm scope | Side-limb yoke (`step_lap_v4`), central limb (`central_limb_v2`), fishy fish |
| Machine handoff | Excel cut programs, manually transferred (unchanged) |

Out of scope for v1: split yoke (currently broken), direct CNC integration,
multi-tenant auth, mobile app (the API makes it possible later).

---

## 1. Architecture

API-first, layered. The "middleware" is a service layer that both the HTTP API and
the MCP server call in-process; clients never touch the domain logic directly.

```
            ┌────────────┐   ┌─────────────┐   ┌─────────────┐
 clients    │ React SPA  │   │ Mobile (v2) │   │ MCP clients │  (Claude, agents)
            └─────┬──────┘   └──────┬──────┘   └──────┬──────┘
                  │   HTTP/JSON (OpenAPI)             │ MCP (stdio / streamable HTTP)
            ┌─────▼─────────────────▼──────┐   ┌──────▼─────────┐
 interface  │ FastAPI app   (sheetcut.api) │   │ MCP server     │
            │ routers, request schemas,    │   │ (sheetcut.     │
            │ auth dependency (stubbed)    │   │  mcp_server)   │
            └──────────────┬───────────────┘   └──────┬─────────┘
                           │      both call           │
            ┌──────────────▼──────────────────────────▼─────────┐
 service    │ sheetcut.services — use cases                     │
            │ ProfileService · GenerationService                │
            │ MachineConfigService · ArtifactService            │
            ├───────────────────────────────────────────────────┤
 domain     │ sheetcut.core — PURE (no I/O, no input(), no      │
            │ paths): pydantic models, algorithms, exporters    │
            ├───────────────────────────────────────────────────┤
 infra      │ SQLite via SQLModel/SQLAlchemy + Alembic          │
            │ artifact store (filesystem dir, swappable to S3)  │
            └───────────────────────────────────────────────────┘
```

Hard rules:

- `core/` imports nothing from `services/`, `api/`, or `mcp_server/`. It is a pure
  function of inputs → cut program. This is what makes web/mobile/MCP equally easy.
- All user interaction (today's `input()` calls and console warnings) becomes either
  request validation errors or structured warnings in responses.
- Persistence choices (SQLite, filesystem artifacts) hide behind the service layer so
  the cloud variant (Postgres, object storage) is a swap, not a rewrite.

## 2. Domain model (pydantic v2)

Formalizes the ad-hoc JSON/dicts that exist today:

| Model | Replaces | Notes |
|---|---|---|
| `ToolSpec` | entries in `cut_program_input/prog_0.json` | name enum (`h`, `v`, `fp45`, `fm45`, `f0`, `s`, `ys`, `fish_head`, `fish_tail`), step_lap_count/distance, open_code, is_skewed |
| `CutProfile` | a whole input JSON file | ordered `ToolSpec` list + profile type + name/id/timestamps |
| `RunParameters` | `data/test_002.json` shape | length_list, slp_dlist, layers, scrap_length, sheet no |
| `MachineConfig` | `gui/config.json` + `Offset` class | versioned calibration record with change history |
| `CutProgram` / `CutStep` | the 15-column Excel output | feed dist, v-notch traverse, tool, indices, sheet count, … |

**Units:** all internal computation in **integer micrometres**; mm only at the API
boundary. This eliminates the float-`==` matching bugs in the current loops
(`fishy_fish.py:122`, `step_lap_v3.py:776`) by construction.

## 3. Repository layout

Monorepo, one Python distribution plus the web app:

```
sheet_cut/
├── pyproject.toml              # uv-managed
├── src/sheetcut/
│   ├── core/
│   │   ├── models.py           # domain models
│   │   ├── units.py            # mm ↔ µm
│   │   ├── algorithms/
│   │   │   ├── side_limb_yoke.py   # port of step_lap_v4.ToolList
│   │   │   ├── central_limb.py     # port of gui/central_limb_v2
│   │   │   └── fishy_fish.py       # port of neo branch FishyFishService
│   │   └── export/
│   │       ├── excel.py        # same 15 columns the operator knows
│   │       └── plot.py         # plot-series JSON (from gui/visualize.py logic)
│   ├── services/
│   ├── db/                     # SQLModel models + Alembic migrations
│   ├── api/                    # FastAPI: main.py, routers/, schemas/
│   └── mcp_server/             # FastMCP tools wrapping services
├── web/                        # Vite + React + TS
├── legacy/                     # current code, frozen — parity oracle
├── tests/
│   ├── golden/                 # recorded legacy outputs
│   └── test_parity_*.py
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## 4. Migration strategy: golden-master parity

The algorithms are the asset and they encode machine knowledge that exists nowhere
else. **Port with an oracle, never rewrite from spec:**

1. **Freeze** — move the current directories under `legacy/` unchanged (plus the
   minimal edits needed to import them headlessly).
2. **Record** — a script drives legacy `ToolList`, `TooList_CL`, and fishy fish with
   an input matrix (seed: `data/test_002.json` / `test_003.json` from the `neo`
   branch, expanded across odd/even step-lap counts, open codes, skew, layers) and
   snapshots the step tables to `tests/golden/*.json`.
3. **Port one algorithm at a time** into `core/`, asserting step-for-step equality
   against the golden files (tolerance 1 µm).
4. **Only after parity passes**, apply intentional behavior fixes — each one as an
   explicit, reviewed diff to the golden files.

Known landmines to resolve during the port (from the code review):

- `step_lap_v3.py` vs `shared/base_tools.py` step-lap logic silently diverged
  (`not not` bug + duplicated branch). **`step_lap_v4` is the oracle** — it is what
  the GUI actually runs; v3 retires with `legacy/`.
- Float equality matching → integer µm (above).
- `terminate = 200` iteration caps in fishy fish → explicit bound derived from coil
  length and pattern count, with a hard error instead of silent truncation.
- Excel parity is asserted on **parsed content** (columns/values), not bytes.

## 5. HTTP API (FastAPI)

```
GET/POST   /api/v1/profiles                  list / create cut profiles
GET/PUT/DEL /api/v1/profiles/{id}
POST       /api/v1/profiles/{id}/generate    body = RunParameters → generation record
GET        /api/v1/generations/{id}          step table (paginated) + stats
GET        /api/v1/generations/{id}/artifact.xlsx
GET        /api/v1/generations/{id}/plot     plot-series JSON for visualization
GET/PUT    /api/v1/machine-config            calibration (PUT creates new version)
GET        /api/v1/machine-config/history
GET        /api/v1/healthz
```

- Generation is **synchronous** — the math runs in milliseconds; no queue/Celery.
  Every generation is persisted (profile snapshot + parameters + artifact), giving an
  audit trail of exactly what was sent to the machine.
- Auth: none on LAN v1, but every router uses a `get_current_user` dependency stub
  from day one, so enabling API-key or OIDC later is one function change. CORS
  configured for the SPA.

## 6. MCP server

Official `mcp` Python SDK (FastMCP). Separate entrypoint `sheetcut-mcp`:
stdio transport for local Claude Desktop/Code, streamable HTTP for LAN use. It calls
the service layer **in-process** (same DB/artifact volume as the API) — fewer moving
parts; can be flipped to an HTTP-client adapter if it ever deploys separately.

Tools:

- `list_profiles()` / `get_profile(id)` / `create_profile(spec)`
- `validate_profile(spec)` → structured errors/warnings (today's console warnings)
- `generate_cut_program(profile_id, run_params)` → stats + generation id
- `get_cut_program_steps(generation_id, page)`
- `get_machine_config()`; config updates stay human-only via the web UI initially

Generated `.xlsx` artifacts are exposed as MCP resources.

## 7. Web frontend (Vite + React + TypeScript)

Pages map 1:1 to today's Tkinter screens:

| Page | Replaces |
|---|---|
| Profile builder (tool sequence editor) | `gui/create_cut_program.py` |
| Run (pick profile, lengths/layers, generate, summary) | `gui/run_screen.py` |
| Verify / visualize (plotly.js from `/plot` JSON, download xlsx) | `gui/verify_output_screen.py`, `gui/visualize.py` |
| Machine parameters (edit calibration, view history) | `gui/update_param.py` |

API client generated from the OpenAPI schema (orval or openapi-typescript) so web —
and later mobile — stay type-locked to the backend. TanStack Query for data fetching.
Built SPA is served by nginx (or the FastAPI app) in compose.

Mobile (v2): same API. Cheapest path is making the SPA a responsive PWA; React
Native is the upgrade path and reuses the generated TS types.

## 8. Infrastructure & quality bar

- **Tooling:** uv, ruff (lint + format), pytest + coverage, mypy (strict on `core/`),
  pre-commit.
- **CI (GitHub Actions):** lint → typecheck → tests → web build; Docker image build
  on tags.
- **Runtime:** docker-compose with the API container (uvicorn) + web, one named
  volume for SQLite DB + artifacts. Documented backup = copy the volume.
- **Config:** pydantic-settings (env vars / `.env`) — kills the cwd-relative path
  fragility; machine calibration lives in the DB, not a JSON file next to the code.
- **Migrations:** Alembic from day one, restricted to SQLite-compatible operations to
  keep the Postgres path open.

## 9. Phases

| Phase | Deliverable | Relative size |
|---|---|---|
| **0 — Foundations** | pyproject/uv/ruff/pytest/CI skeleton; move code to `legacy/`; untrack `.pyc`/`.xlsx`; real README | S |
| **1 — Core extraction** | models + units; golden recorder; port fishy fish → yoke → central limb with parity tests; Excel exporter | **L (the bulk)** |
| **2 — Services + persistence** | SQLite schema (profiles, generations, machine_config history, artifacts), services, artifact store | M |
| **3 — API** | FastAPI routers, OpenAPI polish, compose file, httpx e2e tests | M |
| **4a — MCP server** | FastMCP tools over services | **S (do first — instant client)** |
| **4b — React SPA** | four pages, generated client, plotly visualization | L |
| **5 — Hardening + cutover** | optional API-key auth, volume backup doc, retire Tkinter, archive `legacy/` after a bake period | S |

Sequencing note: 4a (MCP) lands right after Phase 3 in ~a day and gives a usable
client for exercising the whole backend while the SPA is built. Port order in
Phase 1 starts with fishy fish because the `neo` branch already has it as a
service class with parity tests — finish that pattern, then repeat for the other two.

## 10. Risks

- **Algorithm parity** — mitigated by golden tests; `legacy/` stays in-tree as the
  oracle until cutover.
- **Undocumented machine behavior** — some correctness lives only in the owner's
  head; every intentional behavior change is an explicit golden-file diff to review.
- **Solo-dev maintenance** — every dependency must earn its place; deliberately no
  Celery/Redis/Kubernetes. Two containers, one volume.
- **Operator trust** — the Excel column semantics must not drift; parity tests pin
  them.
