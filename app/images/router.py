from fastapi import UploadFile, APIRouter
from app.tasks.tasks import process_pic
import shutil


router = APIRouter(
    prefix="/images",
    tags=["Загрузка картинок"],
)


@router.post("/hotels")
async def add_hotels_image(file_name: int, file: UploadFile):
    img_path = f"app/static/images/{file_name}.webp"
    with open(img_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    process_pic.delay(img_path)

