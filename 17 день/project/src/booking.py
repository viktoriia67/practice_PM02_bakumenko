# Временное хранилище (в реальном проекте здесь будет интеграция с БД)

_bookings_db: dict[int, dict] = {}


def get_booking(booking_id: int) -> dict | None:

    return _bookings_db.get(booking_id)


def get_bookings(room_id: int) -> list[dict]:

    return [b for b in _bookings_db.values() if b['room_id'] == room_id]


def update_booking(booking: dict) -> None:

    _bookings_db[booking['id']] = booking


def cancel_booking(booking_id: int) -> None:
    """

    Отменяет бронирование, изменяя его статус на 'cancelled'.

    """

    booking = get_booking(booking_id)

    if not booking:

        raise ValueError("Booking not found")

    # ИСПРАВЛЕНО: Вместо удаления записи меняем статус на 'cancelled'

    booking['status'] = 'cancelled'

    update_booking(booking)


def is_room_free(room_id: int, check_in: str, check_out: str) -> bool:
    """

    Проверяет, свободен ли номер на указанный диапазон дат.

    """

    bookings = get_bookings(room_id)

    for b in bookings:

        # ИСПРАВЛЕНО: Отмененные бронирования не должны блокировать номер

        if b.get('status') == 'cancelled':

            continue

        # Проверка пересечения интервалов дат

        if b['check_in'] < check_out and b['check_out'] > check_in:

            return False

    return True
