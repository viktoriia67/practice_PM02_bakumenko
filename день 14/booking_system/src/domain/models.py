# src/domain/models.py

import datetime
from typing import Optional

class DomainError(Exception):
    """Базовое исключение для бизнес-логики."""
    pass

class Hotel:
    def __init__(self, id: int, name: str, address: str):
        self.id = id
        self.name = name
        self.address = address

    def __eq__(self, other):
        if not isinstance(other, Hotel):
            return NotImplemented
        return self.id == other.id

class Room:
    def __init__(self, id: int, hotel_id: int, number: str, price_per_night: int):
        self.id = id
        self.hotel_id = hotel_id
        self.number = number
        self.price_per_night = price_per_night

    def __eq__(self, other):
        if not isinstance(other, Room):
            return NotImplemented
        return self.id == other.id

class Booking:
    def __init__(self, id: Optional[int], room_id: int, user_name: str,
                 start_date: datetime.date, end_date: datetime.date, status: str):
        self.id = id
        self.room_id = room_id
        self.user_name = user_name
        self.start_date = start_date
        self.end_date = end_date
        self.status = status  # "CONFIRMED", "CANCELLED"