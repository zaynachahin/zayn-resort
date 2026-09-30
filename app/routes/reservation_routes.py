from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from app.schemas.reservations_schema import ReservationCreate, ReservationDateUpdate, ReservationStatusUpdate, ReservationCreateResponse, ReservationUpdateResponse
from app.services import reservation_service
from app.repositories import reservation_repository
from app.services.reservation_exceptions import (
    CustomerNotFoundError,
    RoomNotFoundError,
    RoomNotAvailableError,
    ReservationNotFoundError,
    InvalidStatusTransitionError,
    InvalidReservationOperationError,
    InvalidReservationDatesError
)

router = APIRouter(
    prefix="/reservations",
    tags = ["Reservations"],
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReservationCreateResponse, summary=" ")
def create_reservation_endpoint(payload: ReservationCreate):
    try:
        result = reservation_service.create_reservation(
            payload.customer_id,
            payload.room_id,
            payload.check_in,
            payload.check_out
        )
        return result

    except InvalidReservationDatesError:
        raise HTTPException(status_code=422, detail="Check_out must be after check_in")
    
    except CustomerNotFoundError:
        raise HTTPException(status_code=404, detail="Customer not found")

    except RoomNotFoundError:
        raise HTTPException(status_code=404, detail="Room not found")

    except RoomNotAvailableError:
        raise HTTPException(status_code=409, detail="Room not available")

@router.patch("/{id}/dates", status_code=status.HTTP_200_OK, response_model= ReservationUpdateResponse, summary=" ")
def update_reservation_dates_endpoint(id:UUID, payload:ReservationDateUpdate):
    try:
        result = reservation_service.update_reservation_dates(
            id,
            payload.check_in,
            payload.check_out
        )
        return result

    except InvalidReservationDatesError:
        raise HTTPException(status_code=422, detail="Check_out must be after check_in")
    
    except ReservationNotFoundError:
        raise HTTPException(status_code=404, detail="Reservation not found")

    except InvalidReservationOperationError:
        raise HTTPException(status_code=409, detail="Cannot update dates of a cancelled or checked_out reservation")

    except RoomNotFoundError:
        raise HTTPException(status_code=404, detail="Room not found")

    except RoomNotAvailableError:
        raise HTTPException(status_code=409, detail="Room not available")

@router.patch("/{id}/status", status_code=status.HTTP_200_OK, response_model= ReservationUpdateResponse, summary=" ")
def update_reservation_status_endpoint(id:UUID, payload:ReservationStatusUpdate):
    try:
        result = reservation_service.update_reservation_status(
            id,
            payload.status
        )
        return result

    except ReservationNotFoundError:
        raise HTTPException(status_code=404, detail="Reservation not found")

    except InvalidStatusTransitionError:
        raise HTTPException(status_code=409, detail="Cannot change status")

@router.get("/{id}", status_code=status.HTTP_200_OK, summary=" ")
def get_reservation_endpoint(id:UUID):
    reservation = reservation_repository.get_reservation_by_id(id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )

    return {
        "reservation_id": reservation["id"],
        "customer_id": reservation["customer_id"],
        "room_id": reservation["room_id"],
        "check_in": reservation["check_in"],
        "check_out": reservation["check_out"],
        "status": reservation["status"],
        "total_amount": reservation["total_amount"]
    }

@router.get("", status_code=status.HTTP_200_OK, summary=" ")
def list_reservations_endpoint():
    reservations = reservation_repository.list_reservations()

    response = []

    for reservation in reservations:
        response.append(
            {
                "reservation_id": reservation["id"],
                "customer_id": reservation["customer_id"],
                "room_id": reservation["room_id"],
                "check_in": reservation["check_in"],
                "check_out": reservation["check_out"],
                "status": reservation["status"],
                "total_amount": reservation["total_amount"]
            }
        )

    return response

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary=" ")
def delete_reservation_endpoint(id: UUID):
    try:
        reservation_service.soft_delete_reservation(id)
    except ReservationNotFoundError:
        raise HTTPException(status_code=404, detail="Reservation not found")