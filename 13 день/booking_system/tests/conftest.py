import pytest
from datetime import date
from src.uow.unit_of_work import InMemoryUnitOfWork
from src.domain.models import Room, Hotel

@pytest.fixture
def uow():
    uow_instance = InMemoryUnitOfWork()
    # Наполняем тестовыми данными
    hotel = uow_instance.hotels.add(
        Hotel(id=1, name="Тестовый Отель", address="ул. Пушкина", phone="123")
    )
    uow_instance.rooms.add(
        Room(id=1, hotel_id=hotel.id, number="101", room_type="Standard", price_per_night=100.0)
    )
    return uow_instance
