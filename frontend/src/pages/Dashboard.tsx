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
    useEffect(() => {
        async function fetchSystemInfo() {
            try {
                const data = await getSystemInfo()
                setSystemInfo(data)
                setError(null)
            } catch {
                setError('Failed to load system information')
            } finally {
                setLoading(false)
            }
        }

        fetchSystemInfo()

        const intervalId = setInterval(fetchSystemInfo, 5000)

        return () => {
            clearInterval(intervalId)
        }
    }, [])
    if (loading) {
        return <p>Loading system information...</p>
    }

    if (error || !systemInfo) {
        return <p>{error ?? 'No system information available'}</p>
    }
    return (
        <div className="dashboard">
            <div className="dashboard-heading">
                <h1>Overview</h1>
                <p>Monitor your infrastructure</p>
            </div>

            <div className="server-status">
                <span className={`status-dot ${error ? 'offline' : 'online'}`} />
                <span>{error ? 'Offline' : 'Online'}</span>
            </div>

            <div className="server-info">
                <span>{systemInfo.hostname}</span>
                <span>
                    {systemInfo.os.system} {systemInfo.os.release}
                </span>
            </div>

            <div className="metrics-grid">
                <MetricCard
                    title="CPU Usage"
                    value={`${systemInfo.cpu.usage_percent}%`}
                    description="Processor utilization"
                    percentage={systemInfo.cpu.usage_percent}
                />

                <MetricCard
                    title="Memory"
                    value={`${formatBytes(systemInfo.memory.used)} / ${formatBytes(systemInfo.memory.total)}`}
                    description="RAM utilization"
                    percentage={systemInfo.memory.usage_percent}
                />

                <MetricCard
                    title="Disk Usage"
                    value={`${formatBytes(systemInfo.disk.used)} / ${formatBytes(systemInfo.disk.total)}`}
                    description="Storage utilization"
                    percentage={systemInfo.disk.usage_percent}
                />

                <MetricCard
                    title="Uptime"
                    value={formatUptime(systemInfo.uptime)}
                    description="System uptime"
                />
            </div>
        </div>
    )
}

export default Dashboard
