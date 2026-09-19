from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.metro_service import MetroService

router = APIRouter(tags=["settings"])


class SettingsUpdate(BaseModel):
    max_transfers: int | None = Field(default=None, ge=0)


@router.get("/settings")
def get_settings():
    with MetroService() as s:
        return s.settings()


@router.put("/settings")
def put_settings(body: SettingsUpdate):
    if body.max_transfers is None:
        raise HTTPException(status_code=422, detail="max_transfers 必填且为非负整数")
    with MetroService() as s:
        return s.update_settings(max_transfers=body.max_transfers)
