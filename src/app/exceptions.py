class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class IncorrectRoomIdError(Exception):
    pass


class TimeOverlapError(Exception):
    pass


class IncorrectBookingIdError(Exception):
    pass


class NoPermissionToDeleteBookingError(Exception):
    pass