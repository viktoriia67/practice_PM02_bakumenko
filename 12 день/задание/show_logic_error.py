def calculate_average_recursive_OLD(node):
    val = node[1]
    children = node[2] if len(node) > 2 else []
    if not children:
        return val

    child_average = [calculate_average_recursive_OLD(child) for child in children]

    # ЛОГИЧЕСКАЯ ОШИБКА:
    # Использование простой формулы усреднения средних значений поддеревьев.
    # Математически среднее от средних не равно истинному среднему значению всех узлов.

    return (val + sum(child_average)) / (1 + len(children))

test_tree_data = [
    "Корень (Департамент)", 100, [
        ["Филиал 1", 120, [
            ["Отдел 1.1", 150]
        ]],
        ["Филиал 2", 80, []]
    ]
]

wrong_result = calculate_average_recursive_OLD(test_tree_data)

print("=== ДЕМОНСТРАЦИЯ ЛОГИЧЕСКОЙ ОШИБКИ ===")
print(f"Реузльтат работы программы: {wrong_result}")
