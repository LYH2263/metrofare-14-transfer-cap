from fastapi import APIRouter
from app.schemas.settings import SettingsUpdate
from app.services.metro_service import MetroService

router = APIRouter(tags=["settings"])

@router.get("/settings")
def get_settings():
    with MetroService() as s:
        return s.settings()

@router.put("/settings")
def put_settings(body: SettingsUpdate):
    with MetroService() as s:
        return s.update_settings({"max_transfers": body.max_transfers})
