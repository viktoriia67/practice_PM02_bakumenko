class DomainError(Exception):
    """Базовое исключение домена"""
    pass

class RoomNotAvailableError(DomainError):
    """Исключение: комната недоступна на выбранные даты"""
    pass

class BookingConflictError(DomainError):
    """Исключение: конфликт дат бронирования"""
    pass

class InvalidDatesError(DomainError):
    """Исключение: невалидные даты"""
    pass

class InvalidPromoCodeError(DomainError):
    """Исключение: промокод недействителен или просрочен"""
    pass
