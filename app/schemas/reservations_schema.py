from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import date
from enum import Enum

class ReservationStatus(str, Enum):
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    
class ReservationCreate(BaseModel):
    customer_id: UUID
    room_id: UUID
    check_in: date
    check_out: date

class ReservationDateUpdate(BaseModel):
    check_in: date
    check_out: date

class ReservationStatusUpdate(BaseModel):
    status: ReservationStatus