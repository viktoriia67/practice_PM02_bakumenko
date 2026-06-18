import pytest
from test_error_code import get_average_fixed, LOG_CACHE, MAX_LOG_SIZE

def test_leaf_node_no_index_error():
    """Проверка устранения IndexError на узлах-листьях"""
    leaf = ["Отдел 1.1", 150]
    assert get_average_fixed(leaf) == 150.0

def test_correct_average_calculation():
    """Проверка математической точности расчёта среднего"""
    test_tree = [
        "Корень", 100, [
            ["Филиал 1", 120, [
                ["Отдел 1.1", 150]
                ]],
            ["Филиал 2", 80, []]
            ]
        ]
    assert get_average_fixed(test_tree) == 112.5

def test_memory_leak_prevention():
    """Проверка защиты от утечки памяти"""

    LOG_CACHE.clear()
    test_tree = ["Узел", 100, []]

    for _ in range(1000):
        get_average_fixed(test_tree)
    assert len(LOG_CACHE) <= MAX_LOG_SIZE
