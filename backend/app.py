"""
UPI Mule Account Detection — FastAPI Backend
Production-grade REST API for real-time mule risk scoring.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Path, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.api.score import score_account, batch_score_accounts
from backend.utils.data_loader import load_transactions, load_accounts, load_devices
from backend.utils.logger import get_logger
from backend.core.graph_analysis import build_transaction_graph
from backend.core.auth import (
    authenticate_user,
    create_user_tokens,
    get_current_active_user,
    verify_token,
    TokenData,
    Token,
    User
)

# ── Logger Setup ──────────────────────────────────────────────────────
logger = get_logger("app")

# ── Rate Limiting Setup ───────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── App Setup ─────────────────────────────────────────────────────────
app = FastAPI(
    title="UPI Mule Detection API",
    description=(
        "Real-time mule account detection engine for UPI ecosystems. "
        "Combines graph analytics, behavioral profiling, device correlation, "
        "temporal analysis, and ML-based anomaly detection."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Configuration (Configurable, not wildcard in production) ─────
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter

# ── Preload data (startup cache) ──────────────────────────────────────
_cache: Dict[str, Any] = {}
_cache_ttl: Dict[str, datetime] = {}
CACHE_DURATION = timedelta(seconds=int(os.getenv("CACHE_DURATION_SECONDS", "300")))


def _get_data() -> tuple:
    """Load and cache data with error handling."""
    try:
        if "txns" not in _cache:
            logger.info("Loading data from CSV files...")
            txns = load_transactions()
            txns["sender"] = txns["sender"].astype(str)
            txns["receiver"] = txns["receiver"].astype(str)
            _cache["txns"] = txns
            _cache["accounts"] = load_accounts()
            _cache["devices"] = load_devices()
            _cache["G"] = build_transaction_graph(txns)
            logger.info(
                f"Data loaded successfully: {len(txns)} transactions, "
                f"{len(_cache['accounts'])} accounts, {len(_cache['devices'])} devices"
            )
        return _cache["txns"], _cache["accounts"], _cache["devices"], _cache["G"]
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        raise HTTPException(status_code=503, detail=f"Data files not found: {e}")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        raise HTTPException(status_code=500, detail="Failed to load data: Server error")


def _get_cached_data(cache_key: str, ttl_seconds: int = 300) -> Optional[Any]:
    """Retrieve cached data if valid."""
    if cache_key in _cache and cache_key in _cache_ttl:
        if datetime.utcnow() < _cache_ttl[cache_key]:
            return _cache[cache_key]
        else:
            # Cache expired
            del _cache[cache_key]
            del _cache_ttl[cache_key]
    return None


def _set_cached_data(cache_key: str, data: Any, ttl_seconds: int = 300) -> None:
    """Store data in cache with TTL."""
    _cache[cache_key] = data
    _cache_ttl[cache_key] = datetime.utcnow() + timedelta(seconds=ttl_seconds)


# ── Models ────────────────────────────────────────────────────────────
class TransactionSimulation(BaseModel):
    """Validation model for transaction simulation."""
    sender: str = Field(..., min_length=1, description="Sender account ID")
    receiver: str = Field(..., min_length=1, description="Receiver account ID")
    amount: float = Field(..., gt=0, description="Transaction amount (must be > 0)")

    @validator("sender", "receiver")
    def validate_account_ids(cls, v: str) -> str:
        """Validate account IDs are non-empty strings."""
        if not v or not isinstance(v, str):
            raise ValueError("Account ID must be a non-empty string")
        return str(v).strip()

    @validator("amount")
    def validate_amount(cls, v: float) -> float:
        """Validate amount is positive."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "sender": "ACC001",
                "receiver": "ACC002",
                "amount": 5000.50
            }
        }


class BatchRequest(BaseModel):
    """Validation model for batch score requests."""
    account_ids: List[str] = Field(..., min_items=1, description="List of account IDs to score")

    @validator("account_ids")
    def validate_account_ids(cls, v: List[str]) -> List[str]:
        """Validate account IDs are non-empty."""
        if not v:
            raise ValueError("account_ids list cannot be empty")
        return [str(acc).strip() for acc in v if acc]

    class Config:
        json_schema_extra = {
            "example": {
                "account_ids": ["ACC001", "ACC002", "ACC003"]
            }
        }



# ── Endpoints ─────────────────────────────────────────────────────────

@app.get("/")
def root() -> Dict[str, Any]:
    """Root endpoint with service info and available endpoints."""
    logger.info("GET /")
    return {
        "service": "UPI Mule Detection API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": [
            "/score/{account_id}",
            "/batch_score",
            "/health",
            "/stats",
            "/simulate",
            "/docs",
        ],
    }


@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Authenticate user and issue JWT tokens."""
    logger.debug(f"POST /auth/login - Login attempt for user: {form_data.username}")
    try:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        tokens = create_user_tokens(user)
        logger.info(f"User {form_data.username} authenticated successfully")
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@app.post("/auth/refresh")
async def refresh_token_endpoint(refresh_token: str) -> Token:
    """Refresh access token using refresh token."""
    logger.debug("POST /auth/refresh - Token refresh requested")
    try:
        token_data = verify_token(refresh_token)
        if not token_data:
            logger.warning("Invalid refresh token")
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Create new user object and issue new tokens
        user = User(username=token_data.username, email=f"{token_data.username}@example.com", full_name=token_data.username, disabled=False)
        tokens = create_user_tokens(user)
        logger.info(f"Token refreshed for user: {token_data.username}")
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")


@app.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """OAuth2-compatible login endpoint for FastAPI docs and clients."""
    logger.debug(f"POST /token - Login attempt for user: {form_data.username}")
    try:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        tokens = create_user_tokens(user)
        logger.info(f"User {form_data.username} authenticated successfully")
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        logger.debug("GET /health - Health check requested")
        txns, accounts, devices, G = _get_data()
        health_response = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "transactions": len(txns),
                "accounts": len(accounts),
                "devices": len(devices),
                "graph_nodes": G.number_of_nodes(),
                "graph_edges": G.number_of_edges(),
            },
        }
        logger.info("Health check passed")
        return health_response
    except HTTPException as e:
        logger.error(f"Health check failed: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in health check: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/accounts")
def get_all_accounts() -> Dict[str, Any]:
    """Get list of all unique accounts in the system."""
    try:
        logger.debug("GET /accounts - Fetching all accounts")
        txns, accounts, devices, G = _get_data()
        unique_accounts = sorted(set(txns["sender"]) | set(txns["receiver"]))
        result = {
            "accounts": unique_accounts,
            "count": len(unique_accounts),
            "timestamp": datetime.utcnow().isoformat(),
        }
        logger.info(f"Retrieved {len(unique_accounts)} unique accounts")
        return result
    except HTTPException as e:
        logger.error(f"Failed to fetch accounts: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch accounts")


@app.get("/score/{account_id}")
async def score(
    account_id: str = Path(..., min_length=1),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Score a single account for mule risk in real-time. Requires authentication."""
    try:
        logger.info(f"GET /score/{account_id} - Scoring account")
        
        if not account_id or not isinstance(account_id, str):
            logger.warning(f"Invalid account_id: {account_id}")
            raise HTTPException(status_code=400, detail="Invalid account_id")
        
        start = time.time()
        txns, accounts, devices, G = _get_data()

        result = score_account(account_id, txns=txns, accounts=accounts, devices=devices, G=G)
        result["response_time_ms"] = round((time.time() - start) * 1000, 2)
        result["timestamp"] = datetime.utcnow().isoformat()
        
        logger.info(f"Account {account_id} scored: risk_score={result['risk_score']}")
        return result
    except HTTPException as e:
        logger.error(f"Score endpoint error for {account_id}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error scoring {account_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to score account")


@app.post("/batch_score")
async def batch_score(
    req: BatchRequest,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Score multiple accounts in a single batch call. Requires authentication."""
    try:
        logger.info(f"POST /batch_score - Scoring {len(req.account_ids)} accounts")
        
        if not req.account_ids:
            logger.warning("Empty account_ids in batch request")
            raise HTTPException(status_code=400, detail="account_ids cannot be empty")
        
        start = time.time()
        txns, accounts, devices, G = _get_data()

        results = batch_score_accounts(req.account_ids, txns, accounts, devices, G)
        
        response = {
            "results": results,
            "count": len(results),
            "response_time_ms": round((time.time() - start) * 1000, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Batch score completed for {len(results)} accounts in {response['response_time_ms']}ms")
        return response
    except HTTPException as e:
        logger.error(f"Batch score error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in batch score: {e}")
        raise HTTPException(status_code=500, detail="Failed to score batch")


@app.get("/stats")
async def stats(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get system-wide risk statistics. Requires authentication."""
    try:
        logger.info(f"GET /stats - Fetching system statistics")
        txns, accounts, devices, G = _get_data()
        unique_accounts = sorted(set(txns["sender"]) | set(txns["receiver"]))
        
        logger.debug(f"Scoring {len(unique_accounts)} accounts for stats")
        results = batch_score_accounts(unique_accounts, txns, accounts, devices, G)

        risk_counts: Dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        total_score = 0
        for res in results.values():
            risk_level = res["risk_level"]
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            total_score += res["risk_score"]

        response = {
            "total_accounts": len(unique_accounts),
            "total_transactions": len(txns),
            "risk_distribution": risk_counts,
            "average_risk_score": round(total_score / max(len(unique_accounts), 1), 1),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Stats retrieved: {len(unique_accounts)} accounts analyzed")
        return response
    except HTTPException as e:
        logger.error(f"Stats endpoint error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


@app.post("/simulate")
def simulate_transaction(txn: TransactionSimulation) -> Dict[str, Any]:
    """
    Simulate scoring for a hypothetical transaction.
    Returns risk assessment for both sender and receiver.
    """
    try:
        logger.info(f"POST /simulate - Simulating transaction: {txn.sender} -> {txn.receiver}, amount: {txn.amount}")
        
        start = time.time()
        txns, accounts, devices, G = _get_data()

        sender_result = score_account(txn.sender, txns=txns, accounts=accounts,
                                       devices=devices, G=G)
        receiver_result = score_account(txn.receiver, txns=txns, accounts=accounts,
                                         devices=devices, G=G)

        # Decision logic
        max_risk = max(sender_result["risk_score"], receiver_result["risk_score"])
        if max_risk >= 70:
            decision = "BLOCK"
            reason = "High mule risk detected"
        elif max_risk >= 40:
            decision = "FLAG"
            reason = "Suspicious pattern — requires monitoring"
        else:
            decision = "ALLOW"
            reason = "Normal risk profile"

        response = {
            "transaction": {
                "sender": txn.sender,
                "receiver": txn.receiver,
                "amount": txn.amount,
            },
            "decision": decision,
            "decision_reason": reason,
            "sender_risk": sender_result,
            "receiver_risk": receiver_result,
            "response_time_ms": round((time.time() - start) * 1000, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Simulation completed: decision={decision}, max_risk={max_risk}")
        return response
    except HTTPException as e:
        logger.error(f"Simulation error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in simulation: {e}")
        raise HTTPException(status_code=500, detail="Simulation failed")


from networkx.readwrite import json_graph

@app.get("/transaction_graph")
async def transaction_graph() -> Dict[str, Any]:
    """Expose transaction graph as nodes and edges for frontend visualization (2-5 min cached). Public endpoint for demo."""
    try:
        logger.debug(f"GET /transaction_graph - Fetching graph data")
        
        # Check cache first
        cached_graph = _get_cached_data("transaction_graph", ttl_seconds=300)
        if cached_graph:
            logger.debug("Returning cached transaction graph")
            cached_graph["cached"] = True
            return cached_graph
        
        logger.debug("Generating fresh transaction graph")
        txns, accounts, devices, G = _get_data()
        graph_data = json_graph.node_link_data(G)
        
        # Enrich nodes with risk scores
        all_accounts = sorted(set(txns["sender"]) | set(txns["receiver"]))
        risk_scores = batch_score_accounts(all_accounts, txns, accounts, devices, G)
        
        for node in graph_data["nodes"]:
            acc = node.get("id") or node.get("name")
            if acc and acc in risk_scores:
                node["risk_score"] = risk_scores[acc]["risk_score"]
                node["risk_level"] = risk_scores[acc]["risk_level"]
        
        response = {
            "nodes": graph_data["nodes"],
            "edges": graph_data["links"],
            "cached": False,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Cache the response for 5 minutes
        _set_cached_data("transaction_graph", response, ttl_seconds=300)
        logger.info(f"Graph computed and cached: {len(response['nodes'])} nodes, {len(response['edges'])} edges")
        
        return response
    except HTTPException as e:
        logger.error(f"Transaction graph error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching transaction graph: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transaction graph")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting UPI Mule Detection API...")
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

