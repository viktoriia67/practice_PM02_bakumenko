from abc import ABC, abstractmethod
from datetime import date
from src.domain.exceptions import InvalidPromoCodeError

class DiscountStrategy(ABC):
    @abstractmethod
    def apply_discount(self, base_price: float, booking_date: date) -> float:
        """Применяет скидку к базовой цене с учетом ограничений"""
        pass

class PercentageDiscountStrategy(DiscountStrategy):
    """Стратегия процентной скидки"""
    def __init__(self, percent: float, min_amount: float, expiry_date: date):
        self.percent = percent
        self.min_amount = min_amount
        self.expiry_date = expiry_date

    def apply_discount(self, base_price: float, booking_date: date) -> float:
        if booking_date > self.expiry_date:
            raise InvalidPromoCodeError("Срок действия промокода истек")
        if base_price < self.min_amount:
            raise InvalidPromoCodeError(
                f"Минимальная сумма бронирования для промокода: {self.min_amount}"
            )
        discount = base_price * (self.percent / 100.0)
        return max(0.0, base_price - discount)

class FlatDiscountStrategy(DiscountStrategy):
    """Стратегия фиксированной скидки в валюте"""
    def __init__(self, amount: float, min_amount: float, expiry_date: date):
        self.amount = amount
        self.min_amount = min_amount
        self.expiry_date = expiry_date

    def apply_discount(self, base_price: float, booking_date: date) -> float:
        if booking_date > self.expiry_date:
            raise InvalidPromoCodeError("Срок действия промокода истек")
        if base_price < self.min_amount:
            raise InvalidPromoCodeError(
                f"Минимальная сумма бронирования для промокода: {self.min_amount}"
            )
        return max(0.0, base_price - self.amount)

# Реестр активных промокодов
PROMO_CODES = {
    "SUMMER10": PercentageDiscountStrategy(
        percent=10.0, min_amount=100.0, expiry_date=date(2026, 9, 1)
    ),
    "CASH50": FlatDiscountStrategy(
        amount=50.0, min_amount=300.0, expiry_date=date(2026, 12, 31)
    )
}

class PricingService:
    @staticmethod
    def calculate_price(
        price_per_night: float, 
        nights: int, 
        promo_code: str = None, 
        booking_date: date = None
    ) -> float:
        base_price = price_per_night * nights
        if not promo_code:
            return base_price

        if promo_code not in PROMO_CODES:
            raise InvalidPromoCodeError("Промокод не существует")

        strategy = PROMO_CODES[promo_code]
        current_date = booking_date or date.today()
        return strategy.apply_discount(base_price, current_date)
