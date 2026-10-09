from pydantic import BaseModel, ConfigDict, Field, field_validator
from uuid import UUID
from datetime import date, datetime
from enum import Enum
from decimal import Decimal

class ReservationStatus(str, Enum):
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

class ReservationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: UUID
    room_id: UUID
    check_in: date
    check_out: date

class ReservationDateUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    check_in: date
    check_out: date

class ReservationStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: ReservationStatus

class ReservationCreateResponse(BaseModel):
    id: UUID
    customer_id: UUID
    room_id: UUID
    check_in: date
    check_out: date
    status: ReservationStatus
    total_amount: Decimal
    created_at: datetime

class ReservationUpdateResponse(BaseModel):
    id: UUID
    customer_id: UUID
    room_id: UUID
    check_in: date
    check_out: date
    status: ReservationStatus
    total_amount: Decimal
    updated_at: datetime