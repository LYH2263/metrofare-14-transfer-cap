from pydantic import BaseModel, Field


class SettingsUpdate(BaseModel):
    max_transfers: int = Field(ge=0)
