from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> None: ...
   
    @abstractmethod
    def update(self, entity: T) -> None: ...

    @abstractmethod
    def find_by_id(self, entity_id: UUID) -> T | None: ...
    
    @abstractmethod
    def find_all(self) -> list[T]: ...
    
    @abstractmethod
    def remove(self, entity_id: UUID) -> None: ...
