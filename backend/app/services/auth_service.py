import os
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional

from bson import ObjectId
from jose import JWTError, jwt
from dotenv import load_dotenv

from app.db.session import get_db

load_dotenv()

# ── Config ───────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production-please!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


# ── Password helpers ─────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    # Hash a password for the first time
    # (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    # Check hashed password. Using bcrypt, the salt is extracted from the hash
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


# ── JWT helpers ──────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ── DB operations ────────────────────────────────────────────────────────────

def get_user_by_username(username: str) -> Optional[dict]:
    db = get_db()
    return db.users.find_one({"username": username})


def register_user(username: str, password: str) -> dict:
    """
    Creates a new user in MongoDB.
    Raises ValueError if username already taken.
    Returns the created user document (without password).
    """
    db = get_db()

    if get_user_by_username(username):
        raise ValueError("Username already taken.")

    user_doc = {
        "username": username,
        "hashed_password": hash_password(password),
        "created_at": datetime.now(timezone.utc),
    }
    result = db.users.insert_one(user_doc)
    return {"id": str(result.inserted_id), "username": username}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Validates credentials.
    Returns the user dict (without password) on success, or None on failure.
    """
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return {"id": str(user["_id"]), "username": user["username"]}