from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..auth import require_owner
from ..settings import get_all_settings, set_setting

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    shop_name: str
    shop_address: str
    shop_phone: str = ""


@router.get("/")
def read_settings(db: Session = Depends(get_db), _: models.User = Depends(require_owner)):
    return get_all_settings(db)


@router.put("/")
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_owner)):
    set_setting(db, "shop_name", payload.shop_name)
    set_setting(db, "shop_address", payload.shop_address)
    set_setting(db, "shop_phone", payload.shop_phone)
    return get_all_settings(db)
