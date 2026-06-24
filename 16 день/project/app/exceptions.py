class EntityNotFoundException(Exception):

    """Вызывается, если запрашиваемый заказ не найден в базе данных."""

    pass



class InvalidOrderStatusException(Exception):

    """Вызывается при попытке установить некорректный статус заказа."""

    pass



class DeliveryCalculationException(Exception):

    """Вызывается при сбоях сети или ошибках внешнего API расчета доставки."""

    pass



class InvalidOrderDataException(Exception):

    """Вызывается при передаче некорректных данных для заказа (например, отрицательное кол-во)."""

    pass
