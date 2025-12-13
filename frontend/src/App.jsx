import { useState, useEffect } from 'react'
import './index.css'

const DEMO_API = 'https://extending-lane-sauce-conflicts.trycloudflare.com'
const AUTOHEAL_API = 'https://museums-displays-smile-coast.trycloudflare.com'

function App() {
    const [health, setHealth] = useState('Checking...')
    const [auditLog, setAuditLog] = useState([])
    const [faultState, setFaultState] = useState({
        error_mode: false,
        latency_mode: false,
        cpu_spike_mode: false,
        healthy: true
    })

    // Poll Audit Log
    useEffect(() => {
        const fetchAudit = async () => {
            try {
                const res = await fetch(`${AUTOHEAL_API}/audit`)
                const data = await res.json()
                setAuditLog(data.reverse())
            } catch (e) {
                console.error("Failed to fetch audit log", e)
            }
        }
        const interval = setInterval(fetchAudit, 2000)
        fetchAudit()
        return () => clearInterval(interval)
    }, [])

    // Poll Health
    useEffect(() => {
        const checkHealth = async () => {
            try {
                const res = await fetch(`${DEMO_API}/health`)
                if (res.ok) setHealth('Healthy')
                else setHealth('Unhealthy (503)')
            } catch (e) {
                setHealth('Down (Connection Refused)')
            }
        }
        const interval = setInterval(checkHealth, 2000)
        checkHealth()
        return () => clearInterval(interval)
    }, [])
    // Generate Traffic (so we have requests to measure)
    useEffect(() => {
        const generateTraffic = async () => {
            try {
                await fetch(`${DEMO_API}/`)
            } catch (e) {
                // Ignore errors (expected when 500 mode is on)
            }
        }
        const interval = setInterval(generateTraffic, 1000)
        return () => clearInterval(interval)
    }, [])

    const toggleFault = async (type) => {
        try {
            const res = await fetch(`${DEMO_API}/fault/${type}`, { method: 'POST' })
            const data = await res.json()
            // Optimistic update or state sync could go here
            alert(`Toggled ${type}`)
        } catch (e) {
            alert(`Failed to toggle ${type}: ${e}`)
        }
    }

    return (
        <div>
            <div className="header">
                <h1>AutoHeal Demo</h1>
                <p>Self-Healing Infrastructure Demonstration</p>
            </div>

            <div className="status-indicator">
                Service Status: <span className={health === 'Healthy' ? 'status-healthy' : 'status-unhealthy'}>{health}</span>
            </div>

            <div className="controls">
                <button onClick={() => toggleFault('error')}>Trigger 500 Errors</button>
                <button onClick={() => toggleFault('latency')}>Trigger Latency (1s+)</button>
                <button onClick={() => toggleFault('unhealthy')}>Trigger Unhealthy Check</button>
            </div>

            <div className="timeline">
                <h3>Audit Timeline</h3>
                {auditLog.length === 0 && <p>No events recorded.</p>}
                {auditLog.map((event, i) => (
                    <div key={i} className="event-row">
                        <span className="event-time">{new Date(event.timestamp).toLocaleString()}</span>
                        <span className={`event-status status-${event.status.replace(' ', '-')}`}>{event.status}</span>
                        <span className="event-details">{event.details}</span>
                    </div>
                ))}
            </div>

            <div style={{ marginTop: '2rem' }}>
                <h3>Metrics (Grafana)</h3>
                <iframe
                    src="https://lamb-moves-generating-head.trycloudflare.com/d-solo/autoheal-dash/autoheal-dashboard?orgId=1&panelId=1&theme=dark"
                    width="100%"
                    height="200"
                    frameBorder="0">
                </iframe>
                <p><small>Note: Grafana iframe requires manual login (admin/admin) in this demo.</small></p>
            </div>
        </div>
    )
}

export default App
