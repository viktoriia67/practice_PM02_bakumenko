import sys
import time

# Глобальный список для накопления логов (Источник утечки памяти)
LOG_CACHE = []

def calculate_average_leaky(node):
    
    LOG_CACHE.append(f"LOG: Обработка {node[0]} в {time.time()}")

    val = node[1]
    children = node[2] if len(node) > 2 else []
    
    if not children:
        return val

    child_averages = [calculate_average_leaky(child) for child in children]

    return (val + sum(child_averages)) / (1 + len(children))

test_tree_data = [
    "Корень (Департамент)", 100, [
        ["Филиал 1", 120, [
            ["Отдел 1.1", 150] # Ошибка IndexError: длина списка 2, нет индекса [2].
         ]],
         ["Филиал 2", 80, []]
    ]
]

print("=== СТАРТ ТЕСТА УТЕЧКИ ПАМЯТИ ===")
print(f"Размер кэша логов в начале: {len(LOG_CACHE)} элементов")

for _ in range(5000):
    calculate_average_leaky(test_tree_data)

print(f"Размер кэша логов в конце: {len(LOG_CACHE)} элементов")
print(f"Объём оперативной памяти под кэш: {sys.getsizeof(LOG_CACHE)} байт")
print("ВЫВОД: Память уходит на хранение логов, кэш бесконечно растёт!")
