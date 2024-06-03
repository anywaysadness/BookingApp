"""Зависимости - Depends"""

from datetime import datetime

from fastapi import Depends, Request
from jose import JWTError, jwt

from app.config import settings
from app.exception import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.users.dao import UsersDAO
from app.users.models import Users


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException
    return token


# Depends - зависимость ОТ функции. Выполнение прерывается если выбрасывается исключение на любом из уровней
async def get_current_user(token: str = Depends(get_token)):
    try:
        # декодирование токена
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        raise IncorrectTokenFormatException
    # Проверка времени экспирации
    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpiredException
    # Проверка идентификатора пользователя
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    # Получение пользователя из базы
    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    return current_user
