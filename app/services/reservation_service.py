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
    RoomNotFoundError,
    RoomNotAvailableError,
    ReservationNotFoundError,
    InvalidStatusTransitionError,
    InvalidReservationOperationError,
    InvalidReservationDatesError
)

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

    conflicting_reservation = reservation_repository.get_conflicting_reservations(room_id, check_out, check_in)

    if conflicting_reservation:
        raise RoomNotAvailableError()

    room_category_id = room[0][4]
    room_category = get_room_category_by_id(room_category_id)
    daily_rate = room_category[0][3]
    reservation_days = (check_out - check_in).days
    total_amount = daily_rate * reservation_days

    reservation_id = reservation_repository.create_reservation(customer_id, room_id, check_in, check_out, total_amount)
    return reservation_id

def update_reservation_dates(id, check_in, check_out):
    _validate_reservation_dates(check_in, check_out)   

    reservation = reservation_repository.get_reservation_by_id(id)

    if not reservation:
        raise ReservationNotFoundError()

    status = reservation[0][5]

    if status in ["cancelled", "checked_out"]:
        raise InvalidReservationOperationError()
    
    room_id = reservation[0][2]
    room = get_room_by_id(room_id)

    if not room:
        raise RoomNotFoundError()

    conflicting_reservation = reservation_repository.get_conflicting_reservations_excluding_id(room_id, id, check_out, check_in)

    if conflicting_reservation:
        raise RoomNotAvailableError()

    room_category_id = room[0][4]
    room_category = get_room_category_by_id(room_category_id)
    daily_rate = room_category[0][3]
    reservation_days = (check_out - check_in).days
    total_amount = daily_rate * reservation_days

    reservation_id = reservation_repository.update_reservation_dates(id, check_in, check_out, total_amount)
    return reservation_id

def update_reservation_status(id, status):
    reservation = reservation_repository.get_reservation_by_id(id)

    if not reservation:
        raise ReservationNotFoundError()

    old_status = reservation[0][5]

    valid_transitions = {
        "confirmed": ["cancelled", "checked_in"],
        "checked_in": ["checked_out"],
        "checked_out": [],
        "cancelled": [],
        }

    if status not in valid_transitions[old_status]:
        raise InvalidStatusTransitionError()

    reservation_id = reservation_repository.update_reservation_status(id, status)
    return reservation_id

def soft_delete_reservation(id):
    reservation = reservation_repository.get_reservation_by_id(id)

    if not reservation:
        raise ReservationNotFoundError()

    reservation_id = reservation_repository.soft_delete_reservation(id)
    return reservation_id