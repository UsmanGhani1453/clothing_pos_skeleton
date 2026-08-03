from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from .. import models
from ..database import get_db
from ..auth import verify_password, hash_password, get_current_user, require_owner

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "cashier"


class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    request.session["user_id"] = user.id
    return {"id": user.id, "username": user.username, "role": user.role}


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user


# --- Owner-only user management ---

@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _: models.User = Depends(require_owner)):
    return db.query(models.User).order_by(models.User.username).all()


@router.post("/users", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _: models.User = Depends(require_owner)):
    existing = db.query(models.User).filter(models.User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    if payload.role not in ("owner", "cashier"):
        raise HTTPException(status_code=400, detail="Role must be 'owner' or 'cashier'")

    new_user = models.User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current: models.User = Depends(require_owner)):
    if user_id == current.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"ok": True}
