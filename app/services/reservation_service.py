from app.repositories.customer_repository import(
    get_customer_by_id
)
from app.repositories.room_repository import(
    get_room_by_id
)
from app.repositories import reservation_repository
from app.repositories.room_category_repository import(
    get_room_category_by_id
)
from app.services.reservation_exceptions import (
    CustomerNotFoundError,
    RoomCategoryNotFoundError,
    RoomNotFoundError,
    RoomNotAvailableError,
    ReservationNotFoundError,
    InvalidStatusTransitionError,
    InvalidReservationOperationError,
    InvalidReservationDatesError,
    ReservationAlreadyDeletedError
)
from app.schemas.reservations_schema import ReservationStatus

def _validate_reservation_dates(check_in, check_out):
    if check_out <= check_in:
        raise InvalidReservationDatesError()

def create_reservation(customer_id, room_id, check_in, check_out):
    _validate_reservation_dates(check_in, check_out)   

    customer = get_customer_by_id(customer_id)

    if not customer:
        raise CustomerNotFoundError()

    room = get_room_by_id(room_id)

    if not room:
        raise RoomNotFoundError()

    room_category = get_room_category_by_id(room["room_category_id"])
    if not room_category:
        raise RoomCategoryNotFoundError()
    
    conflicting_reservation = reservation_repository.get_conflicting_reservations(room_id, check_out, check_in)

    if conflicting_reservation:
        raise RoomNotAvailableError()

    daily_rate = room_category["daily_rate"]
    reservation_days = (check_out - check_in).days
    total_amount = daily_rate * reservation_days

    result = reservation_repository.create_reservation(customer_id, room_id, check_in, check_out, total_amount)
    return result

def update_reservation_dates(id, check_in, check_out):
    _validate_reservation_dates(check_in, check_out)   

    reservation = reservation_repository.get_reservation_by_id(id)

    if not reservation:
        raise ReservationNotFoundError()

    status = reservation["status"]

    if status in [ReservationStatus.CANCELLED, ReservationStatus.CHECKED_OUT]:
        raise InvalidReservationOperationError()
    
    room_id = reservation["room_id"]
    room = get_room_by_id(room_id)

    if not room:
        raise RoomNotFoundError()

    room_category = get_room_category_by_id(room["room_category_id"])
    if not room_category:
        raise RoomCategoryNotFoundError()

    conflicting_reservation = reservation_repository.get_conflicting_reservations_excluding_id(room_id, id, check_out, check_in)

    if conflicting_reservation:
        raise RoomNotAvailableError()

    daily_rate = room_category["daily_rate"]
    reservation_days = (check_out - check_in).days
    total_amount = daily_rate * reservation_days

    result = reservation_repository.update_reservation_dates(id, check_in, check_out, total_amount)
    if not result:
        raise ReservationNotFoundError()
    
    return result

def update_reservation_status(id, status):
    reservation = reservation_repository.get_reservation_by_id(id)

    if not reservation:
        raise ReservationNotFoundError()

    old_status = reservation["status"]

    valid_transitions = {
        ReservationStatus.CONFIRMED: [ReservationStatus.CANCELLED, ReservationStatus.CHECKED_IN],
        ReservationStatus.CHECKED_IN: [ReservationStatus.CHECKED_OUT],
        ReservationStatus.CHECKED_OUT: [],
        ReservationStatus.CANCELLED: [],
        }

    if status not in valid_transitions[old_status]:
        raise InvalidStatusTransitionError()

    result = reservation_repository.update_reservation_status(id, status.value)
    if not result:
        raise ReservationNotFoundError()
    
    return result

def soft_delete_reservation(id):
    reservation = reservation_repository.get_reservation_by_id_including_deleted(id)
    if not reservation:
        raise ReservationNotFoundError()

    result = reservation_repository.soft_delete_reservation(id)
    if not result:
        raise ReservationAlreadyDeletedError()
    
    return result