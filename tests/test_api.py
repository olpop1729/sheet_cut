"""End-to-end HTTP API tests (FastAPI TestClient over a tmp SQLite DB)."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from sheetcut.api.main import create_app
from sheetcut.settings import Settings

SLY_TOOLS: list[dict[str, Any]] = [
    {"name": "fp45", "steplap_type": 1, "steplap_count": 3, "open_code": 1},
    {"name": "h"},
    {"name": "v", "steplap_type": 2, "steplap_count": 3, "open_code": 1},
    {"name": "h"},
    {"name": "fm45", "steplap_type": 1, "steplap_count": 3, "open_code": 2},
]

RUN_BODY = {
    "length_list": [700.0, 900.0, 900.0, 700.0],
    "steplap_distances": [2.0, 1.0, 2.0],
    "layers": 1,
    "start_sheet": 1,
}


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    app = create_app(Settings(data_dir=tmp_path / "data"))
    with TestClient(app) as c:
        yield c


def test_healthz(client: TestClient) -> None:
    body = client.get("/api/v1/healthz").json()
    assert body["status"] == "ok"


def test_profile_crud_and_errors(client: TestClient) -> None:
    created = client.post("/api/v1/profiles", json={"name": "yoke-a", "tools": SLY_TOOLS})
    assert created.status_code == 201
    pid = created.json()["id"]
    assert created.json()["pattern_type"] == 1
    assert created.json()["steplap_tool_count"] == 3

    assert (
        client.post("/api/v1/profiles", json={"name": "yoke-a", "tools": SLY_TOOLS}).status_code
        == 409
    )
    assert client.get("/api/v1/profiles/999").status_code == 404
    bad_tool = client.post("/api/v1/profiles", json={"name": "x", "tools": [{"name": "laser"}]})
    assert bad_tool.status_code == 422

    listed = client.get("/api/v1/profiles").json()
    assert [p["id"] for p in listed] == [pid]

    updated = client.put(f"/api/v1/profiles/{pid}", json={"name": "yoke-b", "tools": SLY_TOOLS})
    assert updated.json()["name"] == "yoke-b"

    assert client.delete(f"/api/v1/profiles/{pid}").status_code == 204
    assert client.get(f"/api/v1/profiles/{pid}").status_code == 404


def test_generate_flow(client: TestClient) -> None:
    pid = client.post("/api/v1/profiles", json={"name": "yoke-a", "tools": SLY_TOOLS}).json()["id"]

    gen = client.post(f"/api/v1/profiles/{pid}/generate", json=RUN_BODY)
    assert gen.status_code == 201
    summary = gen.json()
    gid = summary["id"]
    assert summary["pattern_type"] == 1
    # one separating cut per pattern (the closing fm45 is the next pattern's
    # opener) x three step-lap levels
    assert summary["sheet_count"] == 3
    assert summary["row_count"] > 0

    detail = client.get(f"/api/v1/generations/{gid}").json()
    assert detail["machine_config"]["distance_shear_vnotch"] == 4334.5
    assert detail["start_index"] is not None

    steps = client.get(f"/api/v1/generations/{gid}/steps", params={"limit": 5}).json()
    assert steps["columns"][0] == "Feed Dist"
    assert len(steps["rows"]) == 5
    assert steps["total_rows"] == summary["row_count"]

    artifact = client.get(f"/api/v1/generations/{gid}/artifact.xlsx")
    assert artifact.status_code == 200
    assert artifact.content[:2] == b"PK"
    assert "attachment" in artifact.headers["content-disposition"]

    plot = client.get(f"/api/v1/generations/{gid}/plot").json()
    assert len(plot["events"]) == summary["row_count"]
    assert plot["distances"] == {"shear": 4334.5, "hole": 1250.0, "vnotch": 0.0}
    shear = next(e for e in plot["events"] if e["kind"] == "shear")
    assert shear["cut_x"] == round(shear["position"] - 4334.5, 5)

    listed = client.get("/api/v1/generations").json()
    assert listed[0]["id"] == gid

    # bad run parameters -> domain error mapped to 422
    bad = client.post(
        f"/api/v1/profiles/{pid}/generate",
        json={"length_list": [1.0], "steplap_distances": [2.0, 1.0, 2.0]},
    )
    assert bad.status_code == 422


def test_machine_config_endpoints(client: TestClient) -> None:
    current = client.get("/api/v1/machine-config").json()
    assert current["config"]["offset_fp45"] == 0.75
    assert current["version"] == 1

    updated = client.put(
        "/api/v1/machine-config",
        json={**current["config"], "offset_fp45": 0.8, "comment": "recalibrated"},
    ).json()
    assert updated["config"]["offset_fp45"] == 0.8
    assert updated["version"] == 2

    history = client.get("/api/v1/machine-config/history").json()
    assert [h["version"] for h in history] == [2, 1]


def test_api_key_auth(tmp_path: Path) -> None:
    app = create_app(Settings(data_dir=tmp_path / "data", api_key="sekrit"))
    with TestClient(app) as client:
        assert client.get("/api/v1/profiles").status_code == 401
        assert client.get("/api/v1/profiles", headers={"X-API-Key": "wrong"}).status_code == 401
        ok = client.get("/api/v1/profiles", headers={"X-API-Key": "sekrit"})
        assert ok.status_code == 200
        # healthz stays open for container orchestration
        assert client.get("/api/v1/healthz").status_code == 200
