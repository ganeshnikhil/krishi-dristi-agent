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
import requests
import logging

from app.db.session import get_db

logger = logging.getLogger(__name__)

# Fast in-process cache so tools don't hit MongoDB on every tool call
_cache: dict[str, dict] = {}
_lock = Lock()

# ContextVar propagates correctly across asyncio tasks and thread pools
# (threading.local() would be lost when LangGraph dispatches tools)
_current_user_var: ContextVar[Optional[str]] = ContextVar('current_user', default=None)


def _get_state_from_coords(lat: float, lon: float) -> Optional[str]:
    """Reverse geocode to find state using OpenStreetMap Nominatim API."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'KrishiDristiAgent/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})
        # state could be under state, region, county, etc.
        state = address.get("state") or address.get("region") or address.get("county")
        if state:
            logger.debug(f"Reverse geocode success: ({lat}, {lon}) -> {state}")
        else:
            logger.debug(f"Reverse geocode found no state for: ({lat}, {lon})")
        return state
    except Exception as e:
        logger.error(f"Error reverse geocoding ({lat}, {lon}): {e}")
        return None

def set_user_location(username: str, lat: float, lon: float) -> None:
    """Store (lat, lon, and state) for a user in memory AND persist to MongoDB."""
    state = _get_state_from_coords(lat, lon)
    
    with _lock:
        _cache[username] = {"lat": lat, "lon": lon, "state": state}
        logger.debug(f"Stored in memory cache for {username}: lat={lat}, lon={lon}, state={state}")

    # Persist so the data survives server restarts
    db = get_db()
    db.user_locations.update_one(
        {"username": username},
        {"$set": {"lat": lat, "lon": lon, "state": state}},
        upsert=True,
    )
    logger.debug(f"Stored in MongoDB for {username}: lat={lat}, lon={lon}, state={state}")


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
        lat, lon = doc.get("lat"), doc.get("lon")
        state = doc.get("state")
        with _lock:
            _cache[username] = {"lat": lat, "lon": lon, "state": state}
        return lat, lon

    return None

def get_user_state(username: str) -> Optional[str]:
    """
    Return the state for the given user.
    Checks memory first, then MongoDB.
    Returns None if no state is found.
    """
    with _lock:
        if username in _cache:
            return _cache[username].get("state")
            
    # Try MongoDB
    db = get_db()
    doc = db.user_locations.find_one({"username": username})
    if doc:
        state = doc.get("state")
        with _lock:
            _cache.setdefault(username, {})
            _cache[username]["state"] = state
            if "lat" in doc and "lon" in doc:
                _cache[username]["lat"] = doc["lat"]
                _cache[username]["lon"] = doc["lon"]
        return state

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


def get_active_state() -> Optional[str]:
    """
    Returns the active user's state if we reverse-geocoded it,
    otherwise None.
    """
    user = get_current_user()
    if user:
        return get_user_state(user)
    return None


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
