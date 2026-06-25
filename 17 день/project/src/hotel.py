def is_room_available(bookings: list[dict], check_in: str, check_out: str, room_id: int) -> bool:
    """
    Проверка доступности конкретной комнаты с учётом граничных условий.
    """

    for b in bookings:

        if b['room_id'] == room_id:

            # Если даты пересекаются или заезд оформляется в день выезда предыдущей брони

            if b['check_in'] <= check_out and b['check_out'] >= check_in:

                return False
    return True
