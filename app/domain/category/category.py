from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.category.category_value_objects import CategoryName, HexColor


@dataclass(eq=False, slots=True)
class Category:
    """Entity representing a category in the domain model."""

    id: UUID = field(default_factory=uuid4)
    name: CategoryName
    description: str = ""
    color: HexColor | None = None
    is_archived: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, Category):
            return self.id == obj.id
        return False

    def __hash__(self) -> int:
        return hash((type(self), self.id))
