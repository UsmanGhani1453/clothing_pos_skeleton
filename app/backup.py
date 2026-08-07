import sqlite3
import zipfile
import asyncio
from datetime import datetime
from pathlib import Path

from .database import DB_PATH, USER_DIR

# Store backups in a dedicated folder inside the user's persistent directory
BACKUP_DIR = USER_DIR / "backups"
MAX_BACKUPS = 10  # Keep the last 10 backups to save disk space

def create_backup():
    """Safely clones the active SQLite DB, zips it, and cleans up old backups."""
    if not DB_PATH.exists():
        return
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_backup_db = BACKUP_DIR / f"temp_{timestamp}.db"
    backup_zip_path = BACKUP_DIR / f"shop_db_backup_{timestamp}.zip"
    
    try:
        # Safely copy the SQLite database using the native backup API
        # This prevents corruption if a sale is happening at the exact same moment
        with sqlite3.connect(DB_PATH) as src, sqlite3.connect(temp_backup_db) as dst:
            src.backup(dst)
        
        # Compress the snapshot
        with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            backup_zip.write(temp_backup_db, arcname="shop.db")
            
    finally:
        # Remove the uncompressed temporary file
        if temp_backup_db.exists():
            temp_backup_db.unlink()
    
    # Cleanup old backups
    existing_backups = sorted(BACKUP_DIR.glob("shop_db_backup_*.zip"))
    if len(existing_backups) > MAX_BACKUPS:
        oldest_backups = existing_backups[:-MAX_BACKUPS]
        for old_backup in oldest_backups:
            old_backup.unlink()

async def automated_backup_routine():
    """Runs a backup immediately, then sleeps for 24 hours."""
    while True:
        create_backup()
        # Wait for 24 hours (86400 seconds) before running again
        await asyncio.sleep(86400)