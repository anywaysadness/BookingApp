from pydantic import BaseModel, ConfigDict


class SRoomInfo(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    price: int
    services: list
    quantity: int
    image_id: int
    total_cost: int

    model_config = ConfigDict(from_attributes=True)
