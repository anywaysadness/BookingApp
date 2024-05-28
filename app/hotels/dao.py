from app.dao.base import BaseDAO
from app.hotels.models import Hotels
from app.database import async_session_maker, engine
from sqlalchemy import select
from datetime import date
from app.bookings.models import Bookings
from sqlalchemy import and_, or_, func
from app.hotels.rooms.models import Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    # Поиск отеля по дате и локации
    @classmethod
    async def find_all_hotels_by_parameters(
            cls,
            location: str,
            date_from: date,
            date_to: date,
    ):
        # WITH booked_rooms AS(
        #     SELECT * FROM bookings
        #     WHERE(date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
        # (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        # )
        async with async_session_maker() as session:
            # Получение занятых номеров
            booked_rooms = (
                select(Bookings)
                .where(
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from
                        ),
                    ),

                ).cte("booked_rooms")
            )
        # select
        # hotels.id as "Hotel_id",
        # hotels.name as "Hotel_name",
        # hotels.location as "Hotel_location",
        # hotels.services as "Hotel_service",
        # hotels.rooms_quantity,
        # hotels.image_id,
        # rooms.quantity - count(booked_rooms.room_id) as "rooms_left"
        # from rooms
        # left join booked_rooms ON booked_rooms.room_id = rooms.id
        # left join hotels on hotels.id = rooms.hotel_id
        # where hotels."location" like '%лта%'
        # group by hotels.id, rooms.quantity
        # having (rooms.quantity - count(booked_rooms.room_id)) > 0
        # order by hotels.id ASC
            # Получение свободных номеров
            get_rooms_left = (
                select(
                    Hotels.id.label("id"),
                    Hotels.name.label("name"),
                    Hotels.location.label("location"),
                    Hotels.services.label("services"),
                    Hotels.rooms_quantity.label("rooms_quantity"),
                    Hotels.image_id.label("image_id"),
                    (Hotels.rooms_quantity - func.count(booked_rooms.c.room_id)
                     .filter(booked_rooms.c.room_id.is_not(None)))
                    .label("rooms_left"),
                )
                .select_from(Rooms)
                .join(booked_rooms, Rooms.id == booked_rooms.c.room_id, isouter=True)
                .join(Hotels, Hotels.id == Rooms.hotel_id, isouter=True)
                .where(Hotels.location.like(f"%{location}%"))
                .group_by(Hotels.id)
                .order_by(Hotels.id.asc())
            )
            # print(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))
            rooms_left = await session.execute(get_rooms_left)
            return rooms_left.mappings().all()

    # Поиск всех комнат в отеле по дате
    @classmethod
    async def find_rooms_in_hotel(
            cls,
            hotel_id: int,
            date_from: date,
            date_to: date,
    ):

        # WITH free_bookings AS (
        #     SELECT * FROM bookings
        #     WHERE (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
        #     (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        # )
        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings)
                .where(
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from
                        ),
                    ),

                ).cte("booked_rooms")
            )
            # select
            # rooms.id,
            # rooms.hotel_id,
            # rooms.name,
            # rooms.description,
            # rooms.price,
            # rooms.services,
            # rooms.quantity,
            # rooms.image_id,
            # ((5) * rooms.price) as "total_cost",
            # rooms.quantity - count(free_bookings.room_id) as "rooms_left"
            # from rooms
            # left join free_bookings ON free_bookings.room_id = rooms.id
            # where rooms.hotel_id = 1
            # group by rooms.id

            # Получение
            get_rooms_left = (
                select(
                    Rooms.id.label("id"),
                    Rooms.hotel_id.label("hotel_id"),
                    Rooms.name.label("name"),
                    Rooms.description.label("description"),
                    Rooms.price.label("price"),
                    Rooms.services.label("services"),
                    Rooms.quantity.label("quantity"),
                    Rooms.image_id.label("image_id"),
                    ((date_to - date_from).days * Rooms.price).label("total_cost"),
                    (Rooms.quantity - func.count(booked_rooms.c.room_id)
                     .filter(booked_rooms.c.room_id.is_not(None)))
                    .label("rooms_left")
                )
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .where(Rooms.hotel_id == hotel_id)
                .group_by(Rooms.id)
                .order_by(Rooms.id.asc())
            )
            rooms_left = await session.execute(get_rooms_left)
            return rooms_left.mappings().all()
