from pydantic import BaseModel, ConfigDict, Field, field_validator
from decimal import Decimal
from datetime import date, datetime
from uuid import UUID

class NameValidatorMixin:
    @field_validator("name")
    @classmethod
    def strip_and_validate_name(cls, value):
        if value is None:
            return None
        stripped_name = value.strip()
        if not stripped_name:
            raise ValueError("Name cannot be empty")
        return stripped_name

class RoomCategoryCreate(BaseModel, NameValidatorMixin):
    model_config = ConfigDict(extra="forbid")
    name: str
    capacity: int = Field(gt=0)
    daily_rate: Decimal = Field(gt=0)

class RoomCategoryUpdate(BaseModel, NameValidatorMixin):
    model_config = ConfigDict(extra="forbid")
    name: str
    capacity: int = Field(gt=0)
    daily_rate: Decimal = Field(gt=0)

class RoomCategoryPatch(BaseModel, NameValidatorMixin):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None)
    capacity: int | None = Field(default=None, gt=0)
    daily_rate: Decimal | None = Field(default=None, gt=0)

class RoomCategoryCreateResponse(BaseModel):
    id: UUID
    name: str
    capacity: int
    daily_rate: Decimal
    created_at: datetime

class RoomCategoryUpdateResponse(BaseModel):
    id: UUID
    name: str
    capacity: int
    daily_rate: Decimal
    updated_at: datetime