from sqlalchemy.orm import Session
from . import models

DEFAULTS = {
    "shop_name": "Your Clothing Shop",
    "shop_address": "Main Bazaar, Lahore",
    "shop_phone": "",
}


def get_setting(db: Session, key: str) -> str:
    row = db.query(models.Setting).filter(models.Setting.key == key).first()
    if row:
        return row.value
    return DEFAULTS.get(key, "")


def get_all_settings(db: Session) -> dict:
    return {key: get_setting(db, key) for key in DEFAULTS}


def set_setting(db: Session, key: str, value: str):
    row = db.query(models.Setting).filter(models.Setting.key == key).first()
    if row:
        row.value = value
    else:
        row = models.Setting(key=key, value=value)
        db.add(row)
    db.commit()
