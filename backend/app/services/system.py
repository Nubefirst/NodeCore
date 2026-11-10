import platform
import time

import psutil

from backend.app.schemas.system import (
    CPUInfo,
    DiskInfo,
    MemoryInfo,
    OSInfo,
    SystemInfoResponse,
)


class SystemService:
    @staticmethod
    def get_system_info() -> SystemInfoResponse:
        cpu = CPUInfo(usage_percent=psutil.cpu_percent(interval=None))

        memory = psutil.virtual_memory()

        memory_info = MemoryInfo(
            total=memory.total,
            used=memory.used,
            usage_percent=memory.percent,
        )

        disk = psutil.disk_usage("/")

        disk_info = DiskInfo(
            total=disk.total,
            used=disk.used,
            usage_percent=disk.percent,
        )

        hostname = platform.node()

        os_info = OSInfo(
            system=platform.system(),
            release=platform.release(),
        )

        uptime = int(time.time() - psutil.boot_time())
        return SystemInfoResponse(
            cpu=cpu,
            memory=memory_info,
            disk=disk_info,
            hostname=hostname,
            os=os_info,
            uptime=uptime,
        )
