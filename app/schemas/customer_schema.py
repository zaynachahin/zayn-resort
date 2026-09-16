from pydantic import BaseModel, Field, field_validator
from datetime import date

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
    full_name: str
    date_of_birth: date
    cpf: str
    newsletter_opt_in: bool

class CustomerUpdate(BaseModel, ValidatorMixin):
    full_name: str
    date_of_birth: date
    cpf: str
    newsletter_opt_in: bool

class CustomerPatch(BaseModel, ValidatorMixin):
    full_name: str | None = Field(default=None)
    date_of_birth: date | None = None
    cpf: str | None = Field(default=None)
    newsletter_opt_in: bool | None = None