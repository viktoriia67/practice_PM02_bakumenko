# tests/test_booking_service.py

import datetime
import pytest

# Импортируем из локального файла с реализациями для тестов!
from tests.unit_of_work import InMemoryUnitOfWork

# Импортируем сервис и модели из основного кода приложения
from src.services.booking_service import BookingService, BookingCreateDTO
from src.domain.models import Hotel, Room


def test_find_free_rooms():
    uow = InMemoryUnitOfWork()
    
    # Создаем сервис (ПРАВИЛЬНО - только с uow)
    booking_service = BookingService(uow)
    
    # --- Подготовка данных ---
    hotel = Hotel(id=1, name="Test Hotel", address="City")
    
    # Комната 101 будет занята бронью.
    room_occupied = Room(id=1, hotel_id=1, number="101", price_per_night=1000)
    
    # Комната 102 будет свободна.
    room_free = Room(id=2, hotel_id=1, number="102", price_per_night=1500)
    
    
    
    