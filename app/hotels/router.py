from fastapi import APIRouter, Query
from datetime import date, datetime, timedelta
from app.hotels.schemas import SHotel, SHotelByLocationInfo
from app.hotels.rooms.schemas import SRoomInfo
from app.hotels.dao import HotelDAO

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


# Получение списка отелей по параметрам
@router.get("", status_code=200)
async def get_hotels_by_location_and_time(
        location: str = "",
        date_from: date = Query("2023-06-15", description=f"Например, {datetime.now().date()}"),
        date_to: date = Query("2023-06-25", description=f"Например, {datetime.now().date()}"),
) -> list[SHotelByLocationInfo]:
    hotels = await HotelDAO.find_all_hotels_by_parameters(location=location, date_from=date_from, date_to=date_to)
    return hotels


# Получение списка комнат определенного отеля
@router.get("/{hotel_id}/rooms", status_code=200)
async def get_rooms_by_hotel_id(
        hotel_id: int,
        date_from: date = Query("2023-06-15", description=f"Например, {datetime.now().date()}"),
        date_to: date = Query("2023-06-25", description=f"Например, {datetime.now().date()}"),
):
    rooms = await HotelDAO.find_rooms_in_hotel(hotel_id=hotel_id, date_from=date_from, date_to=date_to)
    return rooms


# Получение конкретного отеля
@router.get("/id/{hotel_id}", status_code=200)
async def get_hotel_by_id(hotel_id: int) -> SHotel:
    return await HotelDAO.find_by_id(hotel_id)







