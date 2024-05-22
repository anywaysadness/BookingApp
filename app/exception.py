from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorrectEmailOrPasswordException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная почта или пароль"


class TokenExpiredException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Истекло время жизни JWT-токена"


class TokenAbsentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "JWT-токен отсутствует"


class IncorrectTokenFormatException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Некорректный формат JWT-токена"


class UserIsNotPresentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED


class RoomCannotBeBooking(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Не осталось свободных номеров"


class BookingCannotBeDelete(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Не возможно удалить данную бронь"
