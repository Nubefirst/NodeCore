import { useEffect, useState } from 'react'
import MetricCard from '../components/MetricCard'
import { getSystemInfo } from '../services/system'
import type { SystemInfo } from '../types/system'
import { formatBytes, formatUptime } from '../utils/formatters'
import './Dashboard.css'

function Dashboard() {
    const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

    useEffect(() => {
        let isActive = true
        let timeoutId: ReturnType<typeof setTimeout>

        async function fetchSystemInfo() {
            try {
                const data = await getSystemInfo()

                if (!isActive) return

                setSystemInfo(data)
                setError(null)
                setLastUpdated(new Date())
            } catch {
                if (!isActive) return

                setError('Failed to load system information')
            } finally {
                if (isActive) {
                    setLoading(false)
                    timeoutId = setTimeout(fetchSystemInfo, 5000)
                }
            }
        }

        fetchSystemInfo()

        return () => {
            isActive = false
            clearTimeout(timeoutId)
        }
    }, [])

    const connectionStatus = error
        ? 'Offline'
        : loading
            ? 'Connecting...'
            : 'Online'

    return (
        <div className="dashboard">
            <div className="dashboard-heading">
                <h1>Overview</h1>
                <p>Monitor your infrastructure</p>
            </div>

            <div className="server-status">
                <span
                    className={`status-dot ${error ? 'offline' : 'online'
                        }`}
                />
                <span>{connectionStatus}</span>
            </div>

            {error && (
                <div className="dashboard-error">
                    {error}. Retrying automatically...
                </div>
            )}

            <div className="server-info">
                <span>{systemInfo?.hostname ?? 'Unknown server'}</span>
                <span>
                    {systemInfo
                        ? `${systemInfo.os.system} ${systemInfo.os.release}`
                        : 'OS information unavailable'}
                </span>
            </div>

            {lastUpdated && (
                <p className="last-updated">
                    Last updated: {lastUpdated.toLocaleTimeString()}
                </p>
            )}

            <div className="metrics-grid">
                <MetricCard
                    title="CPU Usage"
                    value={
                        systemInfo
                            ? `${systemInfo.cpu.usage_percent}%`
                            : '—'
                    }
                    description="Processor utilization"
                    percentage={systemInfo?.cpu.usage_percent}
                />

                <MetricCard
                    title="Memory"
                    value={
                        systemInfo
                            ? `${formatBytes(systemInfo.memory.used)} / ${formatBytes(systemInfo.memory.total)}`
                            : '—'
                    }
                    description="RAM utilization"
                    percentage={systemInfo?.memory.usage_percent}
                />

                <MetricCard
                    title="Disk Usage"
                    value={
                        systemInfo
                            ? `${formatBytes(systemInfo.disk.used)} / ${formatBytes(systemInfo.disk.total)}`
                            : '—'
                    }
                    description="Storage utilization"
                    percentage={systemInfo?.disk.usage_percent}
                />

                <MetricCard
                    title="Uptime"
                    value={
                        systemInfo
                            ? formatUptime(systemInfo.uptime)
                            : '—'
                    }
                    description="System uptime"
                />
            </div>
        </div>
    )
}

export default Dashboard
