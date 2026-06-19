from datetime import date
from typing import List
from src.domain.models import Booking, BookingStatus
from src.domain.exceptions import RoomNotAvailableError, DomainError
from src.dto.booking_dto import BookingCreateDTO, BookingResponseDTO
from src.services.pricing_service import PricingService
from src.uow.unit_of_work import InMemoryUnitOfWork

class BookingService:
    def __init__(self, uow: InMemoryUnitOfWork):
        self.uow = uow

    def create_booking(self, dto: BookingCreateDTO) -> BookingResponseDTO:
        # Проверяем существование комнаты
        room = self.uow.rooms.get_by_id(dto.room_id)
        if not room:
            raise DomainError("Комната не найдена")

        # Проверка пересечения дат (доступности)
        existing_bookings = self.uow.bookings.get_by_room_id(dto.room_id)
        for b in existing_bookings:
            if b.status != BookingStatus.CANCELLED:
                # Пересечение интервалов [start, end]
                if not (dto.end_date <= b.start_date or dto.start_date >= b.end_date):
                    raise RoomNotAvailableError("Комната занята на эти даты")

        # Вычисление стоимости
        nights = (dto.end_date - dto.start_date).days
        total_price = PricingService.calculate_price(
            price_per_night=room.price_per_night,
            nights=nights,
            promo_code=dto.promo_code,
            booking_date=dto.start_date
        )

        # Сохранение сущности
        booking = Booking(
            id=None,
            room_id=dto.room_id,
            user_name=dto.user_name,
            start_date=dto.start_date,
            end_date=dto.end_date,
            total_price=total_price,
            status=BookingStatus.PENDING,
            promo_code=dto.promo_code
        )
        saved_booking = self.uow.bookings.add(booking)
        
        return BookingResponseDTO(
            id=saved_booking.id,
            room_id=saved_booking.room_id,
            user_name=saved_booking.user_name,
            start_date=saved_booking.start_date,
            end_date=saved_booking.end_date,
            total_price=saved_booking.total_price,
            status=saved_booking.status.value,
            promo_code=saved_booking.promo_code
        )

    def cancel_booking(self, booking_id: int) -> bool:
        booking = self.uow.bookings.get_by_id(booking_id)
        if not booking:
            raise DomainError("Бронирование не найдено")
        booking.status = BookingStatus.CANCELLED
        return True
