from threading import Lock
from typing import Optional, Tuple
from contextvars import ContextVar
import requests
import logging

from app.db.session import get_db

logger = logging.getLogger(__name__)

_cache: dict[str, dict] = {}
_lock = Lock()

_current_user_var: ContextVar[Optional[str]] = ContextVar('current_user', default=None)


# ── Validation ─────────────────────────────────────────────────────────

def is_valid_coords(coords: Optional[Tuple[float, float]]) -> bool:
    return (
        coords is not None and
        coords[0] is not None and
        coords[1] is not None
    )


# ── Reverse Geocoding ─────────────────────────────────────────────────

def _get_state_from_coords(lat: float, lon: float) -> Optional[str]:
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'KrishiDristiAgent/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})

        state = address.get("state") or address.get("region") or address.get("county")
        return state

    except Exception as e:
        logger.error(f"Error reverse geocoding ({lat}, {lon}): {e}")
        return None


# ── Set Location ──────────────────────────────────────────────────────

def set_user_location(username: str, lat: float, lon: float) -> None:
    state = _get_state_from_coords(lat, lon)

    with _lock:
        _cache[username] = {"lat": lat, "lon": lon, "state": state}

    db = get_db()
    db.user_locations.update_one(
        {"username": username},
        {"$set": {"lat": lat, "lon": lon, "state": state}},
        upsert=True,
    )


# ── Get Location ──────────────────────────────────────────────────────

def get_user_location(username: str) -> Optional[Tuple[float, float]]:
    # Check cache
    with _lock:
        if username in _cache:
            d = _cache[username]
            coords = (d.get("lat"), d.get("lon"))
            if is_valid_coords(coords):
                return coords

    # Check DB
    db = get_db()
    doc = db.user_locations.find_one({"username": username})

    if doc:
        lat, lon = doc.get("lat"), doc.get("lon")
        state = doc.get("state")

        coords = (lat, lon)
        if is_valid_coords(coords):
            with _lock:
                _cache[username] = {"lat": lat, "lon": lon, "state": state}
            return coords

    return None


# ── Get State ─────────────────────────────────────────────────────────

def get_user_state(username: str) -> Optional[str]:
    with _lock:
        if username in _cache:
            return _cache[username].get("state")

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


# ── Default (Dehradun) ────────────────────────────────────────────────

DEFAULT_LAT = 30.3165
DEFAULT_LON = 78.0322


# ── Context User ──────────────────────────────────────────────────────

def set_current_user(username: str):
    _current_user_var.set(username)


def get_current_user() -> Optional[str]:
    return _current_user_var.get()


# ── Active Context Helpers ────────────────────────────────────────────

def get_active_location() -> Tuple[float, float]:
    user = get_current_user()

    if user is not None:
        coords = get_user_location(user)
        if is_valid_coords(coords):
            return coords

    logger.warning(f"No valid location for user={user}, using Dehradun default")
    return DEFAULT_LAT, DEFAULT_LON


def get_active_state() -> Optional[str]:
    user = get_current_user()
    if user:
        return get_user_state(user)
    return None


# ── Crop Persistence ──────────────────────────────────────────────────

def set_user_crop(username: str, crop: str) -> None:
    with _lock:
        _cache.setdefault(username, {})
        _cache[username]["last_crop"] = crop.lower()

    db = get_db()
    db.user_locations.update_one(
        {"username": username},
        {"$set": {"last_crop": crop.lower()}},
        upsert=True,
    )


def get_user_crop(username: str) -> Optional[str]:
    with _lock:
        crop = _cache.get(username, {}).get("last_crop")
        if crop:
            return crop

    db = get_db()
    doc = db.user_locations.find_one({"username": username}, {"last_crop": 1})

    if doc and "last_crop" in doc:
        crop = doc["last_crop"]

        with _lock:
            _cache.setdefault(username, {})
            _cache[username]["last_crop"] = crop

        return crop

    return None


def get_active_crop() -> Optional[str]:
    user = get_current_user()
    if user:
        return get_user_crop(user)
    return None



# Fix: avoid `if coords` since (None, None) is truthy; explicitly validate lat/lon are not None