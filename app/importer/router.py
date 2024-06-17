from enum import Enum
from app.users.dependencies import get_current_user
from app.users.models import Users
from fastapi import APIRouter, UploadFile, Depends
import csv
import shutil
from app.dao.base import BaseDAO
from app.hotels.models import Hotels

from app.hotels.dao import HotelDAO
from app.bookings.dao import BookingDAO
from app.users.dao import UsersDAO
from app.hotels.rooms.dao import RoomDAO


router = APIRouter(
    prefix="/import",
    tags=["Import and add CSV to DB"],
)


class CustomTypeTable(Enum):
    bookings = "bookings"
    hotels = "hotels"
    rooms = "rooms"
    users = "users"


@router.post("/{table_name}", status_code=201)
async def add_csv_to_db(
        table_name: CustomTypeTable,
        file: UploadFile,
        # user: Users = Depends(get_current_user),
):
    upload_path = f"app/importer/temp_upload/temp.csv"
    with open(f'{upload_path}', "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    with open(f'{upload_path}', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')
        if csvreader:
            for row in csvreader:
                match table_name.value:
                    case "hotels":
                        await HotelDAO.add(
                            name=row['name'],
                            location=row['location'],
                            services=row['services'],
                            rooms_quantity=int(row['rooms_quantity']),
                            image_id=int(row['image_id'])
                        )
                    case "bookings":
                        pass
                    case "users":
                        pass
                    case "rooms":
                        pass
            return f'All add to '
        # for row in csvreader:
        #     await BaseDAO.add(Hotels, row['name'])

        # for row in csvreader:
        #     print(row, '|')

