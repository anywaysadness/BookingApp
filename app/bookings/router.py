from fastapi import APIRouter, Depends
from app.bookings.schemas import SBooking
from app.bookings.dao import BookingDAO
from app.users.models import Users
from app.users.dependencies import get_current_user
from datetime import date
from app.exception import RoomCannotBeBooking, BookingCannotBeDelete


router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("", status_code=200)
async def get_bookings(
        user: Users = Depends(get_current_user)
):
    return await BookingDAO.get_booking_by_user(user_id=user.id)


@router.post("")
async def add_booking(
        room_id: int, date_from: date, date_to: date,
        user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooking


@router.delete("/{booking_id}", status_code=204)
async def delete_booking(
        booking_id: int,
        user: Users = Depends(get_current_user)
):
    check_booking_by_user = await BookingDAO.find_one_or_none(id=booking_id, user_id=user.id)
    if not check_booking_by_user:
        raise BookingCannotBeDelete
    else:
        await BookingDAO.delete_booking_by_user(booking_id, user.id)

