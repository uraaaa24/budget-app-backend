from abc import ABC, abstractmethod

from app.domain.category.category_entity import Category


class CategoryRepository(ABC):
    """Repository interface for Category entities."""

    @abstractmethod
    def add(self, entity: Category) -> None: ...

    @abstractmethod
    def update(self, entity: Category) -> None: ...

    @abstractmethod
    def find_by_id_and_user_id(self, entity_id: str, user_id: str) -> Category | None: ...

    @abstractmethod
    def find_all_by_user_id(self, user_id: str) -> list[Category]: ...

    @abstractmethod
    def find_all_accessible_by_user(self, user_id: str) -> list[Category]: ...

    @abstractmethod
    def remove(self, entity_id: str) -> None: ...
