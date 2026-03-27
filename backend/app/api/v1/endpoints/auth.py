from fastapi import APIRouter, HTTPException, status
from app.schemas.user import UserRegister, UserLogin, TokenOut, UserOut
from app.services.auth_service import register_user, authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new farmer account (Username/Password)",
)
def register(body: UserRegister):
    """
    Create a new user account cleanly.
    - Username should be unique.
    - Password will be hashed securely via `bcrypt`.
    """
    try:
        user = register_user(body.username, body.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/login",
    response_model=TokenOut,
    summary="Login and receive a JWT access token",
)
def login(body: UserLogin):
    """
    Authenticate with `username` + `password`.
    Returns a token to be used for protected requests.
    """
    user = authenticate_user(body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user["username"], "user_id": user["id"]})
    return TokenOut(access_token=token, user=UserOut(**user))
