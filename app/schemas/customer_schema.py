from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date, datetime
from uuid import UUID

class ValidatorMixin:
    @field_validator("full_name")
    @classmethod
    def strip_and_validate_full_name(cls, value):
        if value is None:
            return None
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Field cannot be empty")
        return stripped_value

    @field_validator("cpf")
    @classmethod
    def strip_and_validate_cpf(cls, value):
        if value is None:
            return None
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("CPF cannot be empty")
        if len(stripped_value) != 11:
            raise ValueError("CPF must have exactly 11 digits")
        if not stripped_value.isdigit():
            raise ValueError("CPF must contain only digits")
        return stripped_value



class CustomerCreate(BaseModel, ValidatorMixin):
    model_config = ConfigDict(extra="forbid")
    full_name: str
    date_of_birth: date
    cpf: str
    newsletter_opt_in: bool

class CustomerUpdate(BaseModel, ValidatorMixin):
    model_config = ConfigDict(extra="forbid")
    full_name: str
    date_of_birth: date
    cpf: str
    newsletter_opt_in: bool

class CustomerPatch(BaseModel, ValidatorMixin):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = Field(default=None)
    date_of_birth: date | None = None
    cpf: str | None = Field(default=None)
    newsletter_opt_in: bool | None = None

class CustomerCreateResponse(BaseModel):
    id: UUID
    full_name: str
    date_of_birth: date
    cpf: str
    newsletter_opt_in: bool
    created_at: datetime

class CustomerUpdateResponse(BaseModel):
    id: UUID
    full_name: str
    date_of_birth: date
    cpf: str
    newsletter_opt_in: bool
    updated_at: datetime