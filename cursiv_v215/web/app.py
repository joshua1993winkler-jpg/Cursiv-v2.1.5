"""
Cursiv Board — FastAPI backend.

Auth model (two-ring figure-8):
  /api/login  tries access_gate (local bcrypt) first — issues bridge token.
              Falls back to board.db — issues web token.
  All routes accept any valid signed token.
  Bridge tokens are machine-bound; only the owner's machine can mint them.

Routes:
  GET  /                  substrate UI (or health JSON on Railway)
  GET  /health            JSON health check
  GET  /robots.txt
  GET  /api/posts         public feed (no auth, 30-day window)
  POST /api/register      create account (Railway / non-local only)
  POST /api/login         get a JWT (local: bcrypt gate, remote: board.db)
  GET  /api/me            current user info (auth required)
  POST /api/blast         post a synthesis (auth required)
  DELETE /api/post/{id}   delete own post (auth required)
  GET  /substrate/status
  POST /substrate/activate
  GET  /substrate/weave
  GET  /substrate/address/{node_id}
"""
from __future__ import annotations

import os
import secrets as _secrets_mod
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel, field_validator

_WEB_DIR     = Path(__file__).parent
_UI_FILE     = _WEB_DIR / "substrate_ui.html"
_FLEET_TOKEN = os.environ.get("CURSIV_FLEET_TOKEN", "")

try:
    from cursiv_v215.web.db   import (
        init_db, create_user, get_user_by_username, get_user_by_id,
        get_user_by_device_id, create_post, get_posts, delete_post,
        count_posts_today, upsert_fleet_node, get_fleet_nodes,
    )
    from cursiv_v215.web.auth import (
        hash_password, verify_password,
        create_bridge_token, create_web_token,
        decode_token,
    )
except ImportError:
    from db   import (
        init_db, create_user, get_user_by_username, get_user_by_id,
        get_user_by_device_id, create_post, get_posts, delete_post,
        count_posts_today, upsert_fleet_node, get_fleet_nodes,
    )
    from auth import (
        hash_password, verify_password,
        create_bridge_token, create_web_token,
        decode_token,
    )

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="Cursiv Board API", docs_url=None, redoc_url=None)

_ALLOWED_ORIGINS = os.environ.get(
    "CURSIV_BOARD_ORIGINS",
    ",".join([
        "https://cursiv.winklers-llc.com",
        "https://api.cursiv.winklers-llc.com",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:1969",
        "http://localhost:1969",
        "http://cursiv.local:1969",
    ])
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    init_db()


# ── Auth helpers ──────────────────────────────────────────────────────────────

def _require_auth(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    payload = decode_token(authorization[7:])
    if not payload:
        raise HTTPException(401, "Invalid or expired token")
    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(401, "User not found")
    return user


def _try_access_gate(username: str, password: str) -> bool:
    """Return True if the local bcrypt gate passes for this username+password."""
    try:
        from cursiv_v215.guardian.access_gate import verify_credentials, is_setup_complete
    except ImportError:
        try:
            import sys, os as _os
            sys.path.insert(0, str(Path(__file__).parents[2]))
            from cursiv_v215.guardian.access_gate import verify_credentials, is_setup_complete
        except ImportError:
            return False
    if not is_setup_complete():
        return False
    return verify_credentials(username, password)


def _provision_local_user(username: str) -> dict:
    """
    Ensure a board.db user record exists for the local machine owner.
    Password field is a random token — this account is never verified
    via PBKDF2 (access_gate is the only gate for local logins).
    """
    user = get_user_by_username(username)
    if not user:
        create_user(username, "local$" + _secrets_mod.token_hex(32))
        user = get_user_by_username(username)
    return user


# ── Models ────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def _clean_username(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) < 2 or len(v) > 24:
            raise ValueError("Username must be 2–24 characters")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username: letters, numbers, _ and - only")
        return v

    @field_validator("password")
    @classmethod
    def _check_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class BlastRequest(BaseModel):
    text:   str
    source: str = "broadcast"

    @field_validator("text")
    @classmethod
    def _clean_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Text cannot be empty")
        return v[:2000]

    @field_validator("source")
    @classmethod
    def _clean_source(cls, v: str) -> str:
        return v if v in ("council", "broadcast") else "broadcast"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    if _UI_FILE.exists():
        return FileResponse(_UI_FILE, media_type="text/html")
    return {"status": "ok", "service": "cursiv-board"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "cursiv-board"}


@app.get("/robots.txt", include_in_schema=False)
def robots():
    return PlainTextResponse(
        "User-agent: *\nDisallow: /api/\nDisallow: /substrate/\n"
    )


@app.get("/api/posts")
def feed():
    return {"posts": get_posts(limit=200)}


@app.post("/api/register", status_code=201)
def register(
    body: RegisterRequest,
    x_cursiv_device: str | None = Header(None),
):
    if get_user_by_username(body.username):
        raise HTTPException(409, "Username already taken")
    if x_cursiv_device and get_user_by_device_id(x_cursiv_device):
        raise HTTPException(409, "An account already exists for this installation")
    create_user(body.username, hash_password(body.password), device_id=x_cursiv_device)
    return {"ok": True}


@app.post("/api/login")
def login(body: LoginRequest):
    """
    Single-needlepoint login.

    Tries the local access_gate (bcrypt) first.
    If it passes → issues a bridge token (machine-bound, valid everywhere).
    If access_gate is absent or doesn't match → falls back to board.db PBKDF2.
    """
    if _try_access_gate(body.username, body.password):
        user  = _provision_local_user(body.username)
        token = create_bridge_token(user["id"], user["username"])
        return {"token": token, "username": user["username"], "ring": "bridge"}

    user = get_user_by_username(body.username)
    if not user or not verify_password(body.password, user["pw_hash"]):
        raise HTTPException(401, "Invalid username or password")
    token = create_web_token(user["id"], user["username"])
    return {"token": token, "username": user["username"], "ring": "web"}


@app.get("/api/me")
def me(authorization: str | None = Header(None)):
    user = _require_auth(authorization)
    return {"id": user["id"], "username": user["username"]}


@app.post("/api/blast", status_code=201)
def blast(
    body:          BlastRequest,
    authorization: str | None = Header(None),
    x_cursiv_cli:  str | None = Header(None),
):
    user = _require_auth(authorization)
    if body.source == "council" and not x_cursiv_cli:
        raise HTTPException(403, "Council posts must come from the Cursiv CLI")
    if count_posts_today(user["id"]) >= 4:
        raise HTTPException(429, "Daily limit reached — 4 posts per day max")
    post = create_post(user["id"], user["username"], body.text, body.source)
    return post


@app.delete("/api/post/{post_id}")
def remove_post(post_id: str, authorization: str | None = Header(None)):
    user = _require_auth(authorization)
    if not delete_post(post_id, user["id"]):
        raise HTTPException(404, "Post not found or not yours")
    return {"ok": True}


# ── Substrate layer ───────────────────────────────────────────────────────────

try:
    from cursiv_v215.substrate.activator import get_activator as _get_substrate
    _SUBSTRATE_OK = True
except ImportError:
    _SUBSTRATE_OK = False


class SubstrateRequest(BaseModel):
    synthesis: str
    query:     str = ""
    source:    str = "local"


@app.get("/substrate/status")
def substrate_status():
    if not _SUBSTRATE_OK:
        raise HTTPException(503, "Substrate layer unavailable")
    return _get_substrate().status()


@app.post("/substrate/activate")
def substrate_activate(body: SubstrateRequest):
    if not _SUBSTRATE_OK:
        raise HTTPException(503, "Substrate layer unavailable")
    return _get_substrate().activate(body.synthesis, query=body.query, source=body.source)


@app.get("/substrate/weave")
def substrate_weave(q: str = "", top_k: int = 5):
    if not _SUBSTRATE_OK:
        raise HTTPException(503, "Substrate layer unavailable")
    if not q:
        raise HTTPException(400, "q parameter required")
    hits = _get_substrate().weave(q, top_k=top_k)
    return {"query": q, "resonant": [{"node_id": n, "resonance": r} for n, r in hits]}


@app.get("/substrate/address/{node_id:path}")
def substrate_address(node_id: str):
    if not _SUBSTRATE_OK:
        raise HTTPException(503, "Substrate layer unavailable")
    act  = _get_substrate()
    addr = act.layer.address(node_id)
    node = act.layer.nodes.get(node_id)
    return {
        "node_id":     node_id,
        "address":     addr,
        "exists":      node is not None,
        "weight":      node.weight if node else None,
        "depth":       node.state.get("depth", 0) if node else None,
        "connections": len(node.connections) if node else 0,
    }


# ── Fleet relay ───────────────────────────────────────────────────────────────

def _check_fleet_token(token: str | None) -> None:
    if not _FLEET_TOKEN or token != _FLEET_TOKEN:
        raise HTTPException(403, "Fleet token required")


class HeartbeatRequest(BaseModel):
    machine_id:   str
    machine_name: str
    username:     str
    version:      str
    status:       str = "idle"
    ip_hint:      str | None = None

    @field_validator("machine_id", "machine_name", "username", "version")
    @classmethod
    def _no_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v[:128]

    @field_validator("status")
    @classmethod
    def _valid_status(cls, v: str) -> str:
        return v if v in ("active", "idle", "tray") else "idle"


@app.post("/remote/heartbeat")
def remote_heartbeat(
    body:           HeartbeatRequest,
    x_fleet_token:  str | None = Header(None),
):
    _check_fleet_token(x_fleet_token)
    upsert_fleet_node(
        body.machine_id, body.machine_name, body.username,
        body.version, body.status, body.ip_hint,
    )
    return {"ok": True}


@app.get("/remote/fleet")
def remote_fleet(
    x_fleet_token: str | None = Header(None),
    since:         int        = Query(default=10, ge=1, le=1440),
):
    _check_fleet_token(x_fleet_token)
    nodes = get_fleet_nodes(since_minutes=since)
    return {"nodes": nodes, "count": len(nodes)}
