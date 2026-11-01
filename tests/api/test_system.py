from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.system import (
    CPUInfo,
    DiskInfo,
    MemoryInfo,
    OSInfo,
    SystemInfoResponse,
)


def test_get_system_info_returns_correct_response(monkeypatch):
    system_info = SystemInfoResponse(
        cpu=CPUInfo(usage_percent=25.0),
        memory=MemoryInfo(
            total=16_000_000_000,
            used=8_000_000_000,
            usage_percent=50.0,
        ),
        disk=DiskInfo(
            total=500_000_000_000,
            used=100_000_000_000,
            usage_percent=20.0,
        ),
        hostname="nodecore-test",
        os=OSInfo(
            system="Linux",
            release="6.8.0",
        ),
        uptime=6000,
    )

    monkeypatch.setattr(
        "backend.app.api.v1.system.SystemService.get_system_info",
        lambda: system_info,
    )

    client = TestClient(app)
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert data["cpu"]["usage_percent"] == 25.0

    assert data["memory"]["total"] == 16_000_000_000
    assert data["memory"]["used"] == 8_000_000_000
    assert data["memory"]["usage_percent"] == 50.0

    assert data["disk"]["total"] == 500_000_000_000
    assert data["disk"]["used"] == 100_000_000_000
    assert data["disk"]["usage_percent"] == 20.0

    assert data["hostname"] == "nodecore-test"
    assert data["os"]["system"] == "Linux"
    assert data["os"]["release"] == "6.8.0"
    assert data["uptime"] == 6000
