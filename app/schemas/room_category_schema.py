from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date

class RoomCategoryCreate(BaseModel):
    name: str = Field(min_length=1)
    capacity: int = Field(gt=0)
    daily_rate: Decimal = Field(gt=0)

class RoomCategoryUpdate(BaseModel):
    name: str = Field(min_length=1)
    capacity: int = Field(gt=0)
    daily_rate: Decimal = Field(gt=0)

class RoomCategoryPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    capacity: int | None = Field(default=None, gt=0)
    daily_rate: Decimal | None = Field(default=None, gt=0)