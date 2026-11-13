export function formatBytes(bytes: number): string {
    const gigabytes = bytes / (1024 ** 3)

    return `${gigabytes.toFixed(1)} GB`
}

export function formatUptime(seconds: number): string {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const remainingSeconds = seconds % 60

    if (days > 0) {
        return `${days}d ${hours}h`
    }

    if (hours > 0) {
        return `${hours}h ${minutes}m`
    }

    if (minutes > 0) {
        return `${minutes}m ${remainingSeconds}s`
    }

    return `${remainingSeconds}s`
}
