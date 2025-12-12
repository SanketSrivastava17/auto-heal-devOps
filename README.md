# AutoHeal: Self-Healing Infrastructure Demo

AutoHeal is a demonstration of a self-healing system. It allows you to trigger faults in a service and watch as the system detects the issue and automatically remediates it.

## Architecture

*   **Demo Service**: A Python Flask app that can be broken on demand (500 errors, Latency, Unhealthy).
*   **Prometheus**: Scrapes metrics from the Demo Service.
*   **Alertmanager**: Evaluates rules and sends alerts to the AutoHeal Engine.
*   **AutoHeal Engine**: A Python/FastAPI app that listens for alerts and restarts the Demo Service via Docker.
*   **Frontend**: A React dashboard to control faults and view the remediation timeline.
*   **Grafana**: Visualizes the metrics.

## Quick Start

### Prerequisites
*   Docker and Docker Compose installed.

### Run

```bash
docker compose up --build -d
```

### Access

*   **Dashboard**: [http://localhost:3000](http://localhost:3000)
*   **Grafana**: [http://localhost:3001](http://localhost:3001) (Login: admin/admin)
*   **Prometheus**: [http://localhost:9090](http://localhost:9090)

## How to Demo

1.  Open the **Dashboard** at `http://localhost:3000`.
2.  Observe the **Service Status** is "Healthy".
3.  Click **"Trigger 500 Errors"**.
4.  The status will eventually turn Red.
5.  Wait approx 15-30 seconds.
6.  Prometheus detects the error rate spike -> Fires Alert -> AutoHeal receives Webhook.
7.  AutoHeal restarts the Demo Service.
8.  Observe the **Audit Timeline** on the Dashboard showing "Remediation Started" and "Remediation Complete".
9.  Service Status returns to "Healthy".

## Components

### Demo Service (`/demo-service`)
Exposes `/metrics` and fault injection endpoints `/fault/...`.

### AutoHeal Engine (`/autoheal-engine`)
FastAPI app mounted with Docker socket access.
*   `POST /webhook`: Receives Alertmanager alerts.
*   `GET /audit`: Returns event log.

### Frontend (`/frontend`)
React + Vite app. Polls AutoHeal for audit logs and Demo Service for health.

## Safety Note
The `autoheal-engine` container has access to `/var/run/docker.sock`. In a public environment, this should be restricted or use a simulated remediation mode.
