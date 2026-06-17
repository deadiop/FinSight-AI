from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from backend.database.db import SessionLocal
from backend.models.transaction import User
from backend.utils.auth import get_password_hash, verify_password, create_access_token, decode_access_token

security = HTTPBearer()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Pydantic schemas for request validation
class UserSignupSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)

class UserLoginSchema(BaseModel):
    username: str
    password: str

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Validate bearer token and return the authenticated User model."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignupSchema, db: Session = Depends(get_db)):
    """Register a new user, verifying username and email uniqueness."""
    # Check if username is already taken
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email is already taken (if provided)
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Hash the password using bcrypt
    hashed_pwd = get_password_hash(user_data.password)

    # Create new User database record
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "status": "success",
            "message": "User registered successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(e)}"
        )

@router.post("/login", response_model=TokenResponseSchema)
def login(credentials: UserLoginSchema, db: Session = Depends(get_db)):
    """Authenticate user credentials and return a secure JWT access token."""
    # Retrieve user from database
    user = db.query(User).filter(User.username == credentials.username).first()
    
    # Validate password hash
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Encode token with user details
    token = create_access_token(data={
        "sub": user.username,
        "user_id": user.id
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
