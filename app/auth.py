from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt

from . import models
from .database import get_db


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def ensure_default_owner(db: Session):
    """On first run, create a default owner account if no users exist."""
    if db.query(models.User).count() == 0:
        default_user = models.User(
            username="admin",
            password_hash=hash_password("admin123"),
            role="owner",
        )
        db.add(default_user)
        db.commit()


def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_owner(user: models.User = Depends(get_current_user)):
    if user.role != "owner":
        raise HTTPException(status_code=403, detail="Owner access required")
    return user
