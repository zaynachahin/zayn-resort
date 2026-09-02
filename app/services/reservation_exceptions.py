class CustomerNotFoundError(Exception):
    pass

class RoomNotFoundError(Exception):
    pass

class RoomNotAvailableError(Exception):
    pass

class InvalidStatusTransitionError(Exception):
    pass

class CustomerNotFound(Exception):
    pass

class ReservationNotFoundError(Exception):
    pass

class InvalidReservationOperationError(Exception):
    pass

class InvalidReservationDatesError(Exception):
    pass