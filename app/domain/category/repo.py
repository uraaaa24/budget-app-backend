from abc import abstractmethod

from app.domain.base_repo import BaseRepository
from app.domain.category.category import Category


class CategoryRepository(BaseRepository[Category]):
    """Repository interface for Category entities."""
    
    @abstractmethod
    def find_by_name(self, name: str) -> Category | None: ...
