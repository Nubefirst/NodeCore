from unittest.mock import MagicMock

from backend.app.schemas.system import SystemInfoResponse
from backend.app.services.system import SystemService


def test_get_system_info_returns_correct_data(monkeypatch):
    monkeypatch.setattr(
        "backend.app.services.system.psutil.cpu_percent",
        lambda interval: 25.0,
    )

    monkeypatch.setattr(
        "backend.app.services.system.psutil.virtual_memory",
        lambda: MagicMock(
            total=16_000_000_000,
            used=8_000_000_000,
            percent=50.0,
        ),
    )

    monkeypatch.setattr(
        "backend.app.services.system.psutil.disk_usage",
        lambda path: MagicMock(
            total=500_000_000_000,
            used=100_000_000_000,
            percent=20.0,
        ),
    )

    monkeypatch.setattr(
        "backend.app.services.system.platform.node",
        lambda: "nodecore-test",
    )

    monkeypatch.setattr(
        "backend.app.services.system.platform.system",
        lambda: "Linux",
    )

    monkeypatch.setattr(
        "backend.app.services.system.platform.release",
        lambda: "6.8.0",
    )

    monkeypatch.setattr(
        "backend.app.services.system.time.time",
        lambda: 10_000,
    )

    monkeypatch.setattr(
        "backend.app.services.system.psutil.boot_time",
        lambda: 4_000,
    )

    result = SystemService.get_system_info()

    assert isinstance(result, SystemInfoResponse)

    assert result.cpu.usage_percent == 25.0

    assert result.memory.total == 16_000_000_000
    assert result.memory.used == 8_000_000_000
    assert result.memory.usage_percent == 50.0

    assert result.disk.total == 500_000_000_000
    assert result.disk.used == 100_000_000_000
    assert result.disk.usage_percent == 20.0

    assert result.hostname == "nodecore-test"

    assert result.os.system == "Linux"
    assert result.os.release == "6.8.0"

    assert result.uptime == 6_000
