from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.deps import DB, CurrentUser, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
ph = PasswordHasher()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: DB, response: Response):
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=body.email,
        password_hash=ph.hash(body.password),
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
        path="/api/auth",
    )

    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DB, response: Response):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    try:
        ph.verify(user.password_hash, body.password)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Rehash if needed (argon2 parameter upgrades)
    if ph.check_needs_rehash(user.password_hash):
        user.password_hash = ph.hash(body.password)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
        path="/api/auth",
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser):
    return UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at.isoformat(),
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token", path="/api/auth")
    return {"detail": "Logged out"}
