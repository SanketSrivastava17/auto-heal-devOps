import logging
import time
import random
import threading
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['endpoint'])
HEALTH_STATUS = Gauge('app_health_status', 'Application Health Status (1=Healthy, 0=Unhealthy)')
CPU_USAGE = Gauge('process_cpu_usage', 'Simulated CPU Usage')

# State
class AppState:
    def __init__(self):
        self.error_mode = False
        self.latency_mode = False
        self.cpu_spike_mode = False
        self.healthy = True

state = AppState()
HEALTH_STATUS.set(1)

# Background CPU Spiker
def cpu_load_generator():
    while True:
        if state.cpu_spike_mode:
            # Simulate CPU load
            start = time.time()
            while time.time() - start < 1:
                _ = [x * x for x in range(10000)]
            CPU_USAGE.set(95)
        else:
            CPU_USAGE.set(random.uniform(1, 5))
        time.sleep(1)

threading.Thread(target=cpu_load_generator, daemon=True).start()

@app.before_request
def before_request():
    if state.latency_mode:
        time.sleep(random.uniform(0.5, 2.0))

@app.route('/')
def index():
    if state.error_mode:
        REQUEST_COUNT.labels('GET', '/', '500').inc()
        return "Internal Server Error", 500
    
    REQUEST_COUNT.labels('GET', '/', '200').inc()
    return "Demo Service Operational", 200

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/health')
def health():
    if not state.healthy:
        return "Unhealthy", 503
    return "OK", 200

# Fault Injection Endpoints
@app.route('/fault/error', methods=['POST'])
def toggle_error():
    state.error_mode = not state.error_mode
    logger.info(f"Error Mode toggled: {state.error_mode}")
    return jsonify({"error_mode": state.error_mode})

@app.route('/fault/latency', methods=['POST'])
def toggle_latency():
    state.latency_mode = not state.latency_mode
    logger.info(f"Latency Mode toggled: {state.latency_mode}")
    return jsonify({"latency_mode": state.latency_mode})

@app.route('/fault/cpu', methods=['POST'])
def toggle_cpu():
    state.cpu_spike_mode = not state.cpu_spike_mode
    logger.info(f"CPU Spike Mode toggled: {state.cpu_spike_mode}")
    return jsonify({"cpu_spike_mode": state.cpu_spike_mode})

@app.route('/fault/unhealthy', methods=['POST'])
def toggle_unhealthy():
    state.healthy = not state.healthy
    HEALTH_STATUS.set(1 if state.healthy else 0)
    logger.info(f"Health Status toggled: {state.healthy}")
    return jsonify({"healthy": state.healthy})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
