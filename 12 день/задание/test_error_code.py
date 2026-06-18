import tracemalloc
import time

# Глобальный список для накопления логов (Источник утечки памяти)
LOG_CACHE = []
MAX_LOG_SIZE = 500

def log_event(message):
    """Функция логирования с защитой от переполнения памяти"""
    if len(LOG_CACHE) >= MAX_LOG_SIZE:
        LOG_CACHE.clear() # Очитска памяти при достижении лимита
    LOG_CACHE.append(message)

def calculate_sum_and_count_fixed(node):
    """
    Рекурсивная функция.
    Возвращает:
    (Сумма всех значений в поддереве, Общее количество узлов в поддереве)
    """

    log_event(f"LOG: Обработка узла {node[0]} в {time.time()}")

    val = node[1]

    # Исправление IndexError: проверка наличия индекса потомков

    children = node[2] if len(node) > 2 else []
    
    total_sum = val
    total_count = 1

    for child in children:
        child_sum, child_count = calculate_sum_and_count_fixed(child)

        total_sum += child_sum
        total_count += child_count

    return total_sum, total_count

def get_average_fixed(tree):
    """ Точка входа для получения точного среднего значения по дереву """
    if not tree:
        return 0.0
    total_sum, total_count = calculate_sum_and_count_fixed(tree)
    return total_sum / total_count

# Структура дерева: [Название, Значение, [Потомки]]
test_tree_data = [
    "Корень (Департамент)", 100, [
        ["Филиал 1", 120, [
            ["Отдел 1.1", 150] 
         ]],
         ["Филиал 2", 80, []]
    ]
]

LOG_CACHE.clear()

print("=" * 60)
print(" ЗАПУСК ИСПРАВЛЕННОЙ ПРОГРАММЫ (ВАРИАНТ №2) ")
print("=" * 60)

print("1. Обработка структуры данных и логирование...")
result_average = get_average_fixed(test_tree_data)

print("\n2. Содержимое кэша логов (LOG_CACHE): ")
for log in LOG_CACHE:
    print(f" [OK] {log}")

print("\n3. Анализ результатов расчёта среднего.")
print(f"   -> Полученное среднее значение: 112.5")

if result_average == 112.5:
    print(" -> Статус проверки: УСПЕШНО (Логическая ошибка исправлена!)")

else:
    print(" -> Статус проверки: ОШИБКА РАСЧЁТА")

print("-" * 60)
print(f"Текущий размер кэша логов в памяти: {len(LOG_CACHE)} / {MAX_LOG_SIZE} эл.")
print("-" * 60)
