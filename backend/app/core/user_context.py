"""
user_context.py
--------------
Lightweight in-memory store for per-user coordinates.
The frontend calls POST /api/v1/user/location after login.
All tools import get_user_location() to read the coords instead of
using hardcoded values.
"""
from threading import Lock
from typing import Optional, Tuple
from contextvars import ContextVar
from app.db.session import get_db

# Fast in-process cache so tools don't hit MongoDB on every tool call
_cache: dict[str, dict] = {}
_lock = Lock()

# ContextVar propagates correctly across asyncio tasks and thread pools
# (threading.local() would be lost when LangGraph dispatches tools)
_current_user_var: ContextVar[Optional[str]] = ContextVar('current_user', default=None)


def set_user_location(username: str, lat: float, lon: float) -> None:
    """Store (lat, lon) for a user in memory AND persist to MongoDB."""
    with _lock:
        _cache[username] = {"lat": lat, "lon": lon}

    # Persist so the data survives server restarts
    db = get_db()
    db.user_locations.update_one(
        {"username": username},
        {"$set": {"lat": lat, "lon": lon}},
        upsert=True,
    )


def get_user_location(username: str) -> Optional[Tuple[float, float]]:
    """
    Return (lat, lon) for the given user.
    Checks memory first, then MongoDB.
    Returns None if the user has never set a location.
    """
    with _lock:
        if username in _cache:
            d = _cache[username]
            return d["lat"], d["lon"]

    # Try MongoDB
    db = get_db()
    doc = db.user_locations.find_one({"username": username})
    if doc:
        lat, lon = doc["lat"], doc["lon"]
        with _lock:
            _cache[username] = {"lat": lat, "lon": lon}
        return lat, lon

    return None


# Fallback coordinates (Delhi) used only when no user is set
DEFAULT_LAT = 28.6139
DEFAULT_LON = 77.2090

def set_current_user(username: str):
    """Set the active user for this request/task context."""
    _current_user_var.set(username)

def get_current_user() -> Optional[str]:
    """Get the active user for this request/task context."""
    return _current_user_var.get()

def get_active_location() -> Tuple[float, float]:
    """
    Used by tools. Returns the lat/lon for whoever is currently active.
    Falls back to Delhi if nothing is set.
    """
    user = get_current_user()
    if user:
        coords = get_user_location(user)
        if coords:
            return coords
    return DEFAULT_LAT, DEFAULT_LON


# ── Crop persistence ─────────────────────────────────────────────────────────

def set_user_crop(username: str, crop: str) -> None:
    """Save the last predicted crop for a user (in memory + MongoDB)."""
    with _lock:
        if username not in _cache:
            _cache[username] = {}
        _cache[username]["last_crop"] = crop.lower()

    db = get_db()
    db.user_locations.update_one(
        {"username": username},
        {"$set": {"last_crop": crop.lower()}},
        upsert=True,
    )


def get_user_crop(username: str) -> Optional[str]:
    """
    Return the last predicted crop for the given user.
    Checks memory first, then MongoDB.
    Returns None if no crop has been predicted yet.
    """
    with _lock:
        crop = _cache.get(username, {}).get("last_crop")
        if crop:
            return crop

    db = get_db()
    doc = db.user_locations.find_one({"username": username}, {"last_crop": 1})
    if doc and "last_crop" in doc:
        crop = doc["last_crop"]
        with _lock:
            if username not in _cache:
                _cache[username] = {}
            _cache[username]["last_crop"] = crop
        return crop

    return None


def get_active_crop() -> Optional[str]:
    """Used by tools — returns the current user's last predicted crop, or None."""
    user = get_current_user()
    if user:
        return get_user_crop(user)
    return None
