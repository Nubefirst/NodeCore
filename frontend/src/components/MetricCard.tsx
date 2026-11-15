type MetricCardProps = {
    title: string
    value: string
    description: string
    percentage?: number
}

function MetricCard({
    title,
    value,
    description,
    percentage,
}: MetricCardProps) {
    const getProgressColor = () => {
        if (percentage === undefined) return '#6366f1'

        if (percentage >= 80) return '#ef4444'

        if (percentage >= 60) return '#eab308'

        return '#22c55e'
    }
    return (
        <div className="metric-card">
            <h3>{title}</h3>
            <h2>{value}</h2>
            <p>{description}</p>

            {percentage !== undefined && (
                <div className="metric-progress">
                    <div
                        className="metric-progress-fill"
                        style={{
                            width: `${Math.min(100, Math.max(0, percentage))}%`,
                            backgroundColor: getProgressColor(),
                        }}
                    />
                </div>
            )}
        </div>
    )
}

export default MetricCard
