from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from uuid import UUID

class RoomCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = Field(default=None, min_length=1)
    number: str = Field(min_length=1)
    room_category_id: UUID

class RoomUpdate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = Field(default=None, min_length=1)
    number: str = Field(min_length=1)
    room_category_id: UUID

class RoomPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)
    number: str | None = Field(default=None, min_length=1)
    room_category_id: UUID | None = None