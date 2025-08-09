from dataclasses import dataclass

from app.domain.base_entity import BaseEntity
from app.domain.category.vo import CategoryName, HexColor


@dataclass(eq=False, slots=True)
class Category(BaseEntity):
    """Entity representing a category in the domain model."""
    
    name: CategoryName
    description: str = ""
    color: HexColor | None = None
    is_archived: bool = False
    