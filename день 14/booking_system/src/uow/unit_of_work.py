# src/uow/unit_of_work.py

import datetime
from typing import Protocol, runtime_checkable, List

@runtime_checkable
class WeatherService(Protocol):
    def is_storm(self, date: datetime.date) -> bool: ...

@runtime_checkable
class HotelRepository(Protocol):
    def add(self, hotel) -> None: ...
    def get_by_id(self, hotel_id: int): ...
    def list(self) -> List: ...

@runtime_checkable
class RoomRepository(Protocol):
    def add(self, room) -> None: ...
    def get_by_id(self, room_id: int): ...
    def list(self, hotel_id: int = None) -> List: ...

@runtime_checkable
class BookingRepository(Protocol):
    def add(self, booking) -> None: ...
    def get_by_id(self, booking_id: int): ...
    def list_active_for_room(self, room_id: int, date: datetime.date) -> List: ...

@runtime_checkable
class AbstractUnitOfWork(Protocol):
    hotels: HotelRepository
    rooms: RoomRepository
    bookings: BookingRepository
    weather_service: WeatherService

    def __enter__(self) -> 'AbstractUnitOfWork':
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...