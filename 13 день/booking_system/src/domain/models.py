from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional

class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

@dataclass
class Hotel:
    id: Optional[int]
    name: str
    address: str
    phone: str

@dataclass
class Room:
    id: Optional[int]
    hotel_id: int
    number: str
    room_type: str
    price_per_night: float

@dataclass
class Booking:
    id: Optional[int]
    room_id: int
    user_name: str
    start_date: date
    end_date: date
    total_price: float
    status: BookingStatus = BookingStatus.PENDING
    promo_code: Optional[str] = None

