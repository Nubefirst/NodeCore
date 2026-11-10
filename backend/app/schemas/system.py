from pydantic import BaseModel


class CPUInfo(BaseModel):
    usage_percent: float


class MemoryInfo(BaseModel):
    total: int
    used: int
    usage_percent: float


class DiskInfo(BaseModel):
    total: int
    used: int
    usage_percent: float


class OSInfo(BaseModel):
    system: str
    release: str


class SystemInfoResponse(BaseModel):
    cpu: CPUInfo
    memory: MemoryInfo
    disk: DiskInfo
    hostname: str
    os: OSInfo
    uptime: int
