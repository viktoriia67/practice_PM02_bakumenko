import pytest
from datetime import date
from pydantic import ValidationError
from src.services.booking_service import BookingService
from src.dto.booking_dto import BookingCreateDTO
from src.domain.exceptions import RoomNotAvailableError, InvalidPromoCodeError

def test_successful_booking_without_promo(uow):
    service = BookingService(uow)
    dto = BookingCreateDTO(
        room_id=1,
        user_name="Иван",
        start_date=date(2026, 7, 10),
        end_date=date(2026, 7, 15)  # 5 ночей
    )
    response = service.create_booking(dto)
    assert response.id is not None
    assert response.total_price == 500.0  # 100 * 5

def test_successful_booking_with_percentage_promo(uow):
    service = BookingService(uow)
    dto = BookingCreateDTO(
        room_id=1,
        user_name="Иван",
        start_date=date(2026, 7, 10),
        end_date=date(2026, 7, 15),  # 5 ночей, сумма 500.0
        promo_code="SUMMER10"       # Скидка 10%
    )
    response = service.create_booking(dto)
    assert response.total_price == 450.0  # 500.0 - 10%

def test_expired_promo_code(uow):
    service = BookingService(uow)
    dto = BookingCreateDTO(
        room_id=1,
        user_name="Иван",
        start_date=date(2026, 10, 1), # Промокод SUMMER10 истек 2026-09-01
        end_date=date(2026, 10, 5),
        promo_code="SUMMER10"
    )
    with pytest.raises(InvalidPromoCodeError) as exc:
        service.create_booking(dto)
    assert "истек" in str(exc.value)

def test_min_amount_not_reached(uow):
    service = BookingService(uow)
    dto = BookingCreateDTO(
        room_id=1,
        user_name="Иван",
        start_date=date(2026, 7, 10),
        end_date=date(2026, 7, 12),  # 2 ночи = 200.0 рублей
        promo_code="CASH50"         # Мин. сумма для CASH50 = 300.0 рублей
    )
    with pytest.raises(InvalidPromoCodeError) as exc:
        service.create_booking(dto)
    assert "Минимальная сумма" in str(exc.value)

def test_date_validation_pydantic():
    with pytest.raises(ValidationError):
        BookingCreateDTO(
            room_id=1,
            user_name="Иван",
            start_date=date(2026, 7, 15),
            end_date=date(2026, 7, 10)  # выезд раньше заезда
        )

def test_booking_conflict(uow):
    service = BookingService(uow)
    dto1 = BookingCreateDTO(
        room_id=1,
        user_name="Иван",
        start_date=date(2026, 7, 10),
        end_date=date(2026, 7, 15)
    )
    service.create_booking(dto1)

    dto2 = BookingCreateDTO(
        room_id=1,
        user_name="Петр",
        start_date=date(2026, 7, 12),  # накладывается на предыдущие даты
        end_date=date(2026, 7, 14)
    )
    with pytest.raises(RoomNotAvailableError):
        service.create_booking(dto2)

