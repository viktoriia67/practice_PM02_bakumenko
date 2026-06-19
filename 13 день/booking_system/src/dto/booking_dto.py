from pydantic import BaseModel, Field, field_validator, ValidationInfo
from datetime import date
from typing import Optional

class BookingCreateDTO(BaseModel):
    room_id: int
    user_name: str = Field(..., min_length=2)
    start_date: date
    end_date: date
    promo_code: Optional[str] = None

    @field_validator("end_date")
    @classmethod
    def check_dates(cls, v: date, info: ValidationInfo) -> date:
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("Дата окончания бронирования должна быть позже даты начала")
        return v

class BookingResponseDTO(BaseModel):
    id: int
    room_id: int
    user_name: str
    start_date: date
    end_date: date
    total_price: float
    status: str
    promo_code: Optional[str] = None
