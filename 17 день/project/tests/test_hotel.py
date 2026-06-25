from src.hotel import is_room_available

#Тест 1: Граничные условия (check_in == check_out) в тот же день

def test_is_room_available_edge_case_same_day():

    bookings = [
        
        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-16'}
        
    ]

        #Номер занят 15-го числа, проверяем доступность в этот день

    result = is_room_available(bookings, '2026-06-15', '2026-06-15', 1)

    assert result is False

# Тест успешного бронирования (когда комната свободна)

def test_is_room_available_success():

    bookings = [

        {'room_id': 1, 'check_in': '2026-06-15', 'check_out': '2026-06-16'}

    ]

    # Проверяем другую комнату (должна быть свободна)

    assert is_room_available(bookings, '2026-06-15', '2026-06-16', room_id=2) is True
