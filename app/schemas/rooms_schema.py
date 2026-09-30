from pydantic import BaseModel, ConfigDict, Field, field_validator
from decimal import Decimal
from uuid import UUID
from datetime import date, datetime

class ValidatorMixin:
    @field_validator("name", "number")
    @classmethod
    def strip_and_validate(cls, value):
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be empty")
        return stripped

class OptionalTextValidatorMixin:
    @field_validator("description")
    @classmethod
    def strip_optional(cls, value):
        if value is None:
            return None
        stripped = value.strip()
        return stripped if stripped else None
    
class RoomCreate(BaseModel, ValidatorMixin, OptionalTextValidatorMixin):
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str | None = Field(default=None)
    number: str
    room_category_id: UUID

class RoomUpdate(BaseModel, ValidatorMixin, OptionalTextValidatorMixin):
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str | None = Field(default=None)
    number: str
    room_category_id: UUID

class RoomPatch(BaseModel, ValidatorMixin, OptionalTextValidatorMixin):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    number: str | None = Field(default=None)
    room_category_id: UUID | None = None

class RoomCreateResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    number: str
    room_category_id: UUID
    created_at: datetime

class RoomUpdateResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    number: str
    room_category_id: UUID
    updated_at: datetime