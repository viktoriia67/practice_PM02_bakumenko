import pytest

from src.calculator import calculate_discount, calculate_average_rating



# Тест 1: Отрицательная цена при положительных ночах

def test_calculate_discount_negative_price_positive_nights():

    assert calculate_discount(-100, 3, False) == 0.0



# Тест 2: Положительная цена при нулевых (или отрицательных) ночах

def test_calculate_discount_positive_price_zero_nights():

    assert calculate_discount(1000, 0, False) == 0.0



# Тест 3: Расчет среднего рейтинга с дробными числами

def test_calculate_average_rating_decimals():

    ratings = [4.5, 3.5, 4.0]

    assert calculate_average_rating(ratings) == 4.0



# Тест 4 (Тест-убийца мутаций min -> max): Проверка жесткого лимита скидки в 50%

def test_calculate_discount_max_limit():

    # На границе лимита (30 ночей * 2% = 60%, должно срезаться до 50%)

    result_at_limit = calculate_discount(1000, 30, False)

    assert result_at_limit == 500.0  # Ровно 50% от 1000

    

    # За границей лимита (40 ночей * 2% = 80%, должно срезаться до 50%)

    result_above_limit = calculate_discount(1000, 40, False)

    assert result_above_limit == 500.0  # Должно быть строго 500, а не 800


# Тест для пустого списка рейтингов

def test_calculate_average_rating_empty():

    assert calculate_average_rating([]) == 0.0

