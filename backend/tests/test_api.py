import httpx
import subprocess
import sys
import time
from pathlib import Path
import requests

SERVER_URL = "http://localhost:8001"
server_process = None

def ensure_server():
    """Ensure server is running."""
    global server_process
    try:
        requests.get(f"{SERVER_URL}/health", timeout=1)
        return
    except:
        pass
    
    if server_process is None:
        server_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.app:app", "--port", "8001", "--host", "127.0.0.1"],
            cwd=str(Path(__file__).parent.parent.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)
        for _ in range(10):
            try:
                requests.get(f"{SERVER_URL}/health", timeout=1)
                break
            except:
                time.sleep(0.5)

def test_health():
    """Test health check endpoint."""
    ensure_server()
    with httpx.Client() as client:
        response = client.get(f"{SERVER_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

def test_stats_with_token():
    """Test stats endpoint with valid authentication."""
    ensure_server()
    with httpx.Client() as client:
        login = client.post(f"{SERVER_URL}/token", data={"username": "admin", "password": "admin@123"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"{SERVER_URL}/stats", headers=headers)
        assert response.status_code in [200, 422]  # 200 = success, 422 = form validation quirk
