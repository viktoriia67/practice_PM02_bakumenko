# src/services/booking_service.py

import datetime
from typing import List

from src.domain.models import Booking, DomainError
from src.uow.unit_of_work import AbstractUnitOfWork


class BookingCreateDTO:
    def __init__(
        self,
        room_id: int,
        user_name: str,
        start_date: datetime.date,
        end_date: datetime.date,
    ):
        self.room_id = room_id
        self.user_name = user_name
        self.start_date = start_date
        self.end_date = end_date


class BookingResponseDTO:
    def __init__(self, id: int):
        self.id = id


class BookingService:
    """
    Сервисный слой для управления бронированиями.
    Принимает AbstractUnitOfWork через конструктор.
    """

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def create_booking(self, dto: BookingCreateDTO) -> BookingResponseDTO:
        """Создание нового бронирования."""
        room = self.uow.rooms.get_by_id(dto.room_id)

        if not room:
            raise DomainError("Комната не найдена")

        if dto.start_date >= dto.end_date:
            raise DomainError(
                "Дата окончания должна быть позже даты начала"
            )

        new_booking = Booking(
            id=None,
            room_id=dto.room_id,
            user_name=dto.user_name,
            start_date=dto.start_date,
            end_date=dto.end_date,
            status="CONFIRMED",
        )

        self.uow.bookings.add(new_booking)
        self.uow.commit()

        return BookingResponseDTO(id=new_booking.id)

    def cancel_booking(
        self,
        booking_id: int,
        current_date: datetime.date,
    ):
        """Отмена бронирования с расчетом штрафа."""
        with self.uow:
            booking = self.uow.bookings.get_by_id(booking_id)

            if not booking:
                raise DomainError("Бронирование не найдено")

            if booking.status != "CONFIRMED":
                raise DomainError(
                    "Бронирование уже отменено или завершено"
                )

            is_storm = self.uow.weather_service.is_storm(
                booking.start_date
            )

            fine_amount = 0

            if not is_storm:
                fine_amount = self._calculate_fine(
                    booking.start_date,
                    current_date,
                )

            booking.status = "CANCELLED"

            self.uow.commit()

            return type(
                "CancelResult",
                (),
                {"fine_amount": fine_amount},
            )()

    def find_free_rooms(
        self,
        hotel_id: int,
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> List:
        """Поиск свободных комнат."""

        all_rooms = self.uow.rooms.list(hotel_id=hotel_id)
        free_rooms = []

        for room in all_rooms:
            is_free = True

            current_date = start_date

            while current_date <= end_date:
                active_bookings = (
                    self.uow.bookings.list_active_for_room(
                        room.id,
                        current_date,
                    )
                )

                if active_bookings:
                    is_free = False
                    break

                current_date += datetime.timedelta(days=1)

            if is_free:
                free_rooms.append(room)

        return free_rooms

    def _calculate_fine(
        self,
        start_date: datetime.date,
        current_date: datetime.date,
    ) -> int:
        """
        Простая логика штрафа:
        менее 1 дня до заезда — 1000
        иначе — 0
        """

        days_before_start = (
            start_date - current_date
        ).days

        if days_before_start < 1:
            return 1000

        return 0