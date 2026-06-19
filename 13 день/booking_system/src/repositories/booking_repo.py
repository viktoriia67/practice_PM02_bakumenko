from typing import List, Optional
from src.domain.models import Booking
from src.repositories.base import BaseRepository

class InMemoryBookingRepository(BaseRepository[Booking]):
    def __init__(self):
        self._storage = {}
        self._counter = 1

    def add(self, entity: Booking) -> Booking:
        if entity.id is None:
            entity.id = self._counter
            self._counter += 1
        self._storage[entity.id] = entity
        return entity

    def get_by_id(self, id: int) -> Optional[Booking]:
        return self._storage.get(id)

    def list(self) -> List[Booking]:
        return list(self._storage.values())

    def get_by_room_id(self, room_id: int) -> List[Booking]:
        return [b for b in self._storage.values() if b.room_id == room_id]

    def delete(self, id: int) -> bool:
        if id in self._storage:
            del self._storage[id]
            return True
        return False
