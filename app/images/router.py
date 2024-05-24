from fastapi import UploadFile, APIRouter
import shutil


router = APIRouter(
    prefix="/images",
    tags=["Загрузка картинок"],
)


@router.post("/hotels")
async def add_hotels_image(file_name: int, file: UploadFile):
    with open(f"app/static/images/{file_name}.webp", "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

