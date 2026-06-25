def calculate_discount(price: float, nights: int, is_vip: bool = False) -> float:
    """

    Рассчитывает сумму скидки. Максимальная скидка — 50%.

    """

    # ИСПРАВЛЕНО: Обработка некорректных граничных значений

    if price <= 0 or nights <= 0:

        return 0.0

    # Расчет базовой скидки (например, по 2% за ночь) + VIP бонус

    base_discount = nights * 2

    vip_bonus = 10 if is_vip else 0

    # Ограничение максимальной скидки в 50%

    total_discount = min(base_discount + vip_bonus, 50)

    return price * (total_discount / 100)


def calculate_average_rating(ratings: list[float]) -> float:
    """

    Рассчитывает средний рейтинг.

    """

    if not ratings:

        return 0.0

    return sum(ratings) / len(ratings)
