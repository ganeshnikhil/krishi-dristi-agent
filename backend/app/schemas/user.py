from pydantic import BaseModel, Field

# ── Request bodies ──────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

# ── Response bodies ─────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: str
    username: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
