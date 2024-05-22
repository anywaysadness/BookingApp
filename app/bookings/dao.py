from app.dao.base import BaseDAO
from app.bookings.models import Bookings
from app.hotels.rooms.models import Rooms
from datetime import date
from sqlalchemy import select, insert, delete, func, and_, or_
from app.database import async_session_maker, engine


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(
            cls,
            user_id: int,
            room_id: int,
            date_from: date,
            date_to: date,
    ):

        # WITH booked_rooms AS (
        #     SELECT * FROM bookings
        #     WHERE room_id = 1 AND
        #     (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
        #     (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        # )
        async with async_session_maker() as session:
            # Получение занятых номеров
            booked_rooms = (
                select(Bookings)
                .where(
                    and_(
                        Bookings.room_id == room_id,
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
                    )
                )
                .cte("booked_rooms")
            )

            # SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
            # LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
            # WHERE rooms.id = 1
            # GROUP BY rooms.quantity, booked_rooms.room_id

            # Получение свободных номеров
            get_rooms_left = (
                select(
                    (Rooms.quantity - func.count(booked_rooms.c.room_id).filter(booked_rooms.c.room_id.is_not(None)))
                    .label("rooms_left")
                )
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .where(Rooms.id == room_id)
                .group_by(Rooms.quantity, booked_rooms.c.room_id)
            )
            # print(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))
            rooms_left = await session.execute(get_rooms_left)
            rooms_left: int = rooms_left.scalar()
            # Если есть свободные
            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = (
                    insert(Bookings)
                    .values(
                        user_id=user_id,
                        room_id=room_id,
                        date_from=date_from,
                        date_to=date_to,
                        price=price,
                    )
                    .returning(
                        Bookings.id,
                        Bookings.user_id,
                        Bookings.room_id,
                        Bookings.date_from,
                        Bookings.date_to,
                    )
                )

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.mappings().one()
            else:
                return None

    @classmethod
    async def get_booking_by_user(
            cls,
            user_id: int,
    ):
        # select * from bookings
        # join rooms on rooms.id = bookings.room_id
        # where bookings.user_id = 5
        async with async_session_maker() as session:
            get_full_booking_by_user = (
                select(
                    Bookings.room_id.label("Room_id"),
                    Bookings.user_id.label("User_id"),
                    Bookings.date_from.label("Date_from"),
                    Bookings.date_to.label("Date_to"),
                    Bookings.price.label("Price"),
                    Bookings.total_cost.label("Total_cost"),
                    Bookings.total_days.label("Total_days"),
                    Rooms.image_id.label("Image_id"),
                    Rooms.name.label("Name"),
                    Rooms.description.label("Desc"),
                    Rooms.services.label("Services")
                )
                .select_from(Bookings)
                .join(Rooms, Rooms.id == Bookings.room_id, isouter=True)
                .where(Bookings.user_id == user_id)
                .order_by(Bookings.id)
            )
            booking_by_user = await session.execute(get_full_booking_by_user)
            return booking_by_user.mappings().all()

    @classmethod
    async def delete_booking_by_user(
        cls,
        booking_id: int,
        user_id: int,
    ):

        async with async_session_maker() as session:
            # delete from bookings
            # where bookings.id = 19
            delete_booking = (
                delete(Bookings)
                .where(
                    and_(
                        Bookings.id == booking_id,
                        Bookings.user_id == user_id
                    ),
                )
            )
            # print(delete_booking.compile(engine, compile_kwargs={"literal_binds": True}))
            delete_booking = await session.execute(delete_booking)
            await session.commit()
