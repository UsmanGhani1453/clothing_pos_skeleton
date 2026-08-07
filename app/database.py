from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import secrets
from pathlib import Path

# Create a persistent directory in the user's home folder
USER_DIR = Path.home() / ".clothing_pos"
USER_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = USER_DIR / "shop.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SESSION_SECRET_PATH = USER_DIR / "session_secret.key"


def get_session_secret() -> str:
    """Load the session-signing secret from disk, creating it on first run.

    This must stay the same across server restarts, otherwise every login
    session becomes invalid (and looks like a random "Not authenticated"
    error) the moment the app restarts.
    """
    if SESSION_SECRET_PATH.exists():
        secret = SESSION_SECRET_PATH.read_text().strip()
        if secret:
            return secret

    secret = secrets.token_hex(32)
    SESSION_SECRET_PATH.write_text(secret)
    return secret