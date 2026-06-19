from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> T:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass

    @abstractmethod
    def list(self) -> List[T]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
