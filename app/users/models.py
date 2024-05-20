from sqlalchemy import Column, Integer, String
from app.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=True)
    email = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)