from pydantic import BaseModel, ConfigDict, Json


class SHotel(BaseModel):
    id: int
    name: str
    location: str
    services: list
    rooms_quantity: int
    image_id: int

    model_config = ConfigDict(from_attributes=True)
