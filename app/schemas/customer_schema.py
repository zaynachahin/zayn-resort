from pydantic import BaseModel, Field
from datetime import date

class CustomerCreate(BaseModel):
    full_name: str
    date_of_birth: date
    cpf: str = Field(min_length=11, max_length=11)
    newsletter_opt_in: bool