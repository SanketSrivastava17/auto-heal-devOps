import logging
import docker
import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoHeal")
app = FastAPI()

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Docker Client

# Environment (URL of the Demo Service)
import os
DEMO_SERVICE_URL = os.getenv("DEMO_SERVICE_URL", "http://demo-service:5000")

# Audit Log Store
audit_log = []

class WebhookPayload(BaseModel):
    alerts: List[dict]

@app.get("/")
def home():
    return {"status": "AutoHeal Engine Running"}

@app.get("/audit")
def get_audit_log():
    return audit_log

def log_event(action, details, status):
    event = {
        "timestamp": datetime.datetime.now().isoformat(),
        "action": action,
        "details": details,
        "status": status
    }
    audit_log.append(event)
    # Keep last 50 events
    if len(audit_log) > 50:
        audit_log.pop(0)

    logger.info("Executing Remediation: Soft Reset Demo Service")
    log_event("Remediation Started", "High Error Rate detected. Sending Reset command...", "In Progress")
    
    import requests
    try:
        requests.post(f"{DEMO_SERVICE_URL}/reset")
        log_event("Remediation Complete", "Service reset successfully via API.", "Resolved")
        logger.info("Demo Service soft reset.")
    except Exception as e:
        log_event("Remediation Failed", str(e), "Failed")
        logger.error(f"Failed to reset service: {e}")

def remediate_high_latency():
    logger.info("Executing Remediation: Scaling Up (Simulated)")
    log_event("Remediation Started", "High Latency detected. Scaling up resources...", "In Progress")
    # Simulation: In a real scenario we'd scale up. 
    # Here we just log it, or call the 'latency' toggle on the app to fix it if we want to be fancy.
    # Let's try to "fix" it by calling the app to disable latency mode? 
    # Or just let it be manual? The requirement says "AutoHeal engine remediate automatically".
    # Let's call the app to turn off latency mode as a "fix".
    
    import requests
    try:
        requests.post("http://demo-service:5000/fault/latency") # Toggle it off
        log_event("Remediation Complete", "Scaled up resources (Latency injection disabled).", "Resolved")
    except Exception as e:
        log_event("Remediation Failed", f"Failed to scale: {e}", "Failed")

def remediate_unhealthy():
    logger.info("Executing Remediation: Service Unhealthy")
    log_event("Remediation Started", "Service Unhealthy. Sending Reset command...", "In Progress")
    
    import requests
    try:
        requests.post(f"{DEMO_SERVICE_URL}/reset")
        log_event("Remediation Complete", "Service reset successfully via API.", "Resolved")
    except Exception as e:
        log_event("Remediation Failed", str(e), "Failed")

@app.post("/webhook")
async def webhook(payload: dict):
    logger.info(f"Received Webhook: {payload}")
    
    alerts = payload.get('alerts', [])
    for alert in alerts:
        status = alert.get('status')
        if status == 'resolved':
            continue
            
        labels = alert.get('labels', {})
        alert_name = labels.get('alertname')
        
        logger.info(f"Processing Alert: {alert_name}")
        
        if alert_name == 'HighErrorRate':
            remediate_high_error_rate()
        elif alert_name == 'HighLatency':
            remediate_high_latency()
        elif alert_name == 'InstanceUnhealthy':
            remediate_unhealthy()
            
    return {"status": "processed"}
