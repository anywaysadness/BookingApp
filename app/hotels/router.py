from fastapi import APIRouter
from datetime import date
from app.hotels.schemas import SHotel
from app.hotels.dao import HotelDAO

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get("/{location}")
async def get_hotels_by_location_and_time(location: str) -> list[SHotel]:
    return await HotelDAO.find_all(name=location)

