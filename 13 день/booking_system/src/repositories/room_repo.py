from typing import List, Optional
from src.domain.models import Room
from src.repositories.base import BaseRepository

class InMemoryRoomRepository(BaseRepository[Room]):
    def __init__(self):
        self._storage = {}
        self._counter = 1

    def add(self, entity: Room) -> Room:
        if entity.id is None:
            entity.id = self._counter
            self._counter += 1
        self._storage[entity.id] = entity
        return entity

    def get_by_id(self, id: int) -> Optional[Room]:
        return self._storage.get(id)

    def list(self) -> List[Room]:
        return list(self._storage.values())

    def get_by_hotel_id(self, hotel_id: int) -> List[Room]:
        return [r for r in self._storage.values() if r.hotel_id == hotel_id]

    def delete(self, id: int) -> bool:
        if id in self._storage:
            del self._storage[id]
            return True
        return False
