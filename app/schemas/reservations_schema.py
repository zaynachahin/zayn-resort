from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from datetime import date

class ReservationCreate(BaseModel):
    customer_id: UUID
    room_id: UUID
    check_in: date
    check_out: date

class ReservationDateUpdate(BaseModel):
    check_in: date
    check_out: date

class ReservationStatusUpdate(BaseModel):
    status: str = Field(min_length=1)