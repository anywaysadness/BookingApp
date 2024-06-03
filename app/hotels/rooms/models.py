from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Rooms(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, nullable=True)
    hotel_id = Column(ForeignKey("hotels.id"), nullable=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=True)
    services = Column(JSON, nullable=True)
    quantity = Column(Integer, nullable=True)
    image_id = Column(Integer)

    hotel = relationship("Hotels", back_populates="room")
    booking = relationship("Bookings", back_populates="room")

    def __str__(self):
        return f"Комната {self.name}"
