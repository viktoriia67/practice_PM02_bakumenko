# tests/unit_of_work.py

import datetime
from typing import List, Dict

# Импортируем протоколы из основного модуля проекта
from src.uow.unit_of_work import AbstractUnitOfWork, HotelRepository, RoomRepository, BookingRepository, WeatherService

# --- Реализации репозиториев в памяти ---
class InMemoryHotelRepository(HotelRepository):
    def __init__(self):
        self.hotels = {}
    def add(self, hotel):
        self.hotels[hotel.id] = hotel
    def get_by_id(self, hotel_id):
        return self.hotels.get(hotel_id)
    def list(self):
        return list(self.hotels.values())

class InMemoryRoomRepository(RoomRepository):
    def __init__(self):
        self.rooms = {}
    def add(self, room):
        self.rooms[room.id] = room
    def get_by_id(self, room_id):
        return self.rooms.get(room_id)
    def list(self, hotel_id=None):
        if hotel_id is None:
            return list(self.rooms.values())
        return [room for room in self.rooms.values() if room.hotel_id == hotel_id]

class InMemoryBookingRepository(BookingRepository):
    def __init__(self):
        self.bookings = {}
    def add(self, booking):
        # Генерируем ID для бронирования (в памяти это просто инкремент)
        if booking.id is None:
            booking.id = len(self.bookings) + 1
        self.bookings[booking.id] = booking
    def get_by_id(self, booking_id):
        return self.bookings.get(booking_id)
    def list_active_for_room(self, room_id: int, date: datetime.date) -> List:
        return [
            b for b in self.bookings.values()
            if b.room_id == room_id and b.status != "CANCELLED"
            and b.start_date <= date <= b.end_date # Проверка на пересечение дат
        ]

# --- Реализация Unit of Work ---
class InMemoryUnitOfWork(AbstractUnitOfWork):
    """
    Реализация Unit of Work для тестов.
    Хранит данные в словарях в оперативной памяти.
    """
    def __init__(self):
        self.hotels = InMemoryHotelRepository()
        self.rooms = InMemoryRoomRepository()
        self.bookings = InMemoryBookingRepository()
        
        # По умолчанию используем Mock для погоды.
        # В conftest и тестах мы его заменим на нужный нам.
        from unittest.mock import Mock
        self.weather_service = Mock()
        
    def __enter__(self):
        return self

    def __exit__(self, *args):
         # В InMemory реализации откат - это просто очистка данных.
         # Это гарантирует чистоту тестов друг от друга.
         self.rollback()

    def commit(self):
         pass # В памяти коммит ничего не делает

    def rollback(self):
         # Полная очистка репозиториев для чистоты следующего теста.
         self.hotels = InMemoryHotelRepository()
         self.rooms = InMemoryRoomRepository()
         self.bookings = InMemoryBookingRepository()