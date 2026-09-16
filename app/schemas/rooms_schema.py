from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from uuid import UUID

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
    name: str
    description: str | None = Field(default=None)
    number: str
    room_category_id: UUID

class RoomUpdate(BaseModel, ValidatorMixin, OptionalTextValidatorMixin):
    name: str
    description: str | None = Field(default=None)
    number: str
    room_category_id: UUID

class RoomPatch(BaseModel, ValidatorMixin, OptionalTextValidatorMixin):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    number: str | None = Field(default=None)
    room_category_id: UUID | None = None