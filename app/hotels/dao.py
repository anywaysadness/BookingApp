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

    @classmethod
    async def find_all_by_parameters(
            cls,
            location: str,
            date_from: date,
            date_to: date,
    ):
        # WITH free_bookings AS(
        #     SELECT * FROM bookings
        #     WHERE(date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
        # (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        # )
        async with async_session_maker() as session:
            free_bookings = (
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

                ).cte("free_bookings")
            )
        # select
        # hotels.id as "Hotel_id",
        # hotels.name as "Hotel_name",
        # hotels.location as "Hotel_location",
        # hotels.services as "Hotel_service",
        # hotels.rooms_quantity,
        # hotels.image_id,
        # rooms.quantity - count(free_bookings.room_id) as "rooms_left"
        # from rooms
        # left join free_bookings ON free_bookings.room_id = rooms.id
        # left join hotels on hotels.id = rooms.hotel_id
        # where hotels."location" like '%лта%'
        # group by hotels.id, rooms.quantity
        # having (rooms.quantity - count(free_bookings.room_id)) > 0
        # order by hotels.id ASC

            get_rooms_left = (
                select(
                    Hotels.id.label("Hotel_id"),
                    Hotels.name.label("Hotel_name"),
                    Hotels.location.label("Hotel_location"),
                    Hotels.services.label("Hotel_service"),
                    Hotels.rooms_quantity,
                    Hotels.image_id,
                    (Rooms.quantity - func.count(free_bookings.c.room_id)
                     .filter(free_bookings.c.room_id.is_not(None)))
                    .label("rooms_left")
                )
                .select_from(Rooms)
                .join(free_bookings, free_bookings.c.room_id == Rooms.id, isouter=True)
                .join(Hotels, Hotels.id == Rooms.hotel_id, isouter=True)
                .where(Hotels.location.like(f"%{location}%"))
                .group_by(Hotels.id, Rooms.quantity)
                .having(Rooms.quantity - func.count(free_bookings.c.room_id)
                        .filter(free_bookings.c.room_id.is_not(None)) > 0)
                .order_by(Hotels.id.asc())
            )
            # print(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))
            rooms_left = await session.execute(get_rooms_left)
            return rooms_left.mappings().all()
