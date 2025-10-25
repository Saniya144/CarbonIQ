from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from passlib.hash import bcrypt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.models import User
import os

router = APIRouter()

# ------------------------------
# JWT Configuration
# ------------------------------

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")  # change this later!

access_security = JwtAccessBearer(secret_key=SECRET_KEY)

# ------------------------------
# Request Models
# ------------------------------

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# ------------------------------
# Routes
# ------------------------------

@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Registers a new user in the database."""
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = bcrypt.hash(user.password)
    new_user = User(email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"msg": "User created successfully"}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Logs in a user and returns an access token."""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not bcrypt.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create access token
    access_token = access_security.create_access_token(subject={"user_id": db_user.id})
    return {"access_token": access_token, "user_id": db_user.id}

# Example protected route
@router.get("/me")
def get_profile(credentials: JwtAuthorizationCredentials = Depends(access_security)):
    """Returns the current user's info (decoded from JWT)."""
    return {"user_id": credentials.subject["user_id"]}
