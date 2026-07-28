from pydantic import BaseModel, Field
from datetime import date

class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=1)
    date_of_birth: date
    cpf: str = Field(min_length=11, max_length=11)
    newsletter_opt_in: bool

class CustomerUpdate(BaseModel):
    full_name: str = Field(min_length=1)
    date_of_birth: date
    cpf: str = Field(min_length=11, max_length=11)
    newsletter_opt_in: bool