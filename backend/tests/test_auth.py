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

def test_login_success():
    """Test successful login with valid credentials."""
    ensure_server()
    with httpx.Client() as client:
        response = client.post(f"{SERVER_URL}/token", data={"username": "admin", "password": "admin@123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

def test_login_failure():
    """Test failed login with invalid password."""
    ensure_server()
    with httpx.Client() as client:
        response = client.post(f"{SERVER_URL}/token", data={"username": "admin", "password": "wrongpass"})
        assert response.status_code == 401

def test_protected_endpoint_with_token():
    """Test accessing protected endpoints with valid token."""
    ensure_server()
    with httpx.Client() as client:
        login = client.post(f"{SERVER_URL}/token", data={"username": "admin", "password": "admin@123"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"{SERVER_URL}/score/ACC001", headers=headers)
        assert response.status_code == 200
