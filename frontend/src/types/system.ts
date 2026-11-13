export interface SystemInfo {
    cpu: {
        usage_percent: number
    }

    memory: {
        total: number
        used: number
        usage_percent: number
    }

    disk: {
        total: number
        used: number
        usage_percent: number
    }

    hostname: string

    os: {
        system: string
        release: string
    }

    uptime: number
}
