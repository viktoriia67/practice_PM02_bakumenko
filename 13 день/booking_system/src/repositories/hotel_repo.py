from typing import List, Optional
from src.domain.models import Hotel
from src.repositories.base import BaseRepository

class InMemoryHotelRepository(BaseRepository[Hotel]):
    def __init__(self):
        self._storage = {}
        self._counter = 1

    def add(self, entity: Hotel) -> Hotel:
        if entity.id is None:
            entity.id = self._counter
            self._counter += 1
        self._storage[entity.id] = entity
        return entity

    def get_by_id(self, id: int) -> Optional[Hotel]:
        return self._storage.get(id)

    def list(self) -> List[Hotel]:
        return list(self._storage.values())

    def delete(self, id: int) -> bool:
        if id in self._storage:
            del self._storage[id]
            return True
        return False
