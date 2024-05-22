from fastapi import APIRouter
from datetime import date
from app.hotels.schemas import SHotel
from app.hotels.dao import HotelDAO

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


# Получение списка отелей по параметрам
@router.get("/{location}", status_code=200)
async def get_hotels_by_location_and_time(location: str,
                                          date_from: date = '2023-05-15',
                                          date_to: date = '2023-06-20'):
    return await HotelDAO.find_all_hotels_by_parameters(location=location, date_from=date_from, date_to=date_to)


# Получение списка комнат определенного отеля
@router.get("/{hotel_id}/rooms", status_code=200)
async def get_rooms_by_hotel_id(hotel_id: int,
                                date_from: date = '2023-05-15',
                                date_to: date = '2023-06-20'):
    return await HotelDAO.find_rooms_in_hotel(hotel_id=hotel_id, date_from=date_from, date_to=date_to)


# Получение конкретного отеля
@router.get("/id/{hotel_id}", status_code=200)
async def get_hotel_by_id(hotel_id: int) -> SHotel:
    return await HotelDAO.find_by_id(hotel_id)







