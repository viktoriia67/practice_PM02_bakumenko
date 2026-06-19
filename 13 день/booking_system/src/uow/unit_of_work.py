from src.repositories.hotel_repo import InMemoryHotelRepository
from src.repositories.room_repo import InMemoryRoomRepository
from src.repositories.booking_repo import InMemoryBookingRepository

class InMemoryUnitOfWork:
    def __init__(self):
        self.hotels = InMemoryHotelRepository()
        self.rooms = InMemoryRoomRepository()
        self.bookings = InMemoryBookingRepository()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
