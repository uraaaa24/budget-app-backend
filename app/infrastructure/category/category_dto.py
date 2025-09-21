from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.category.category_entity import Category
from app.domain.category.category_value_objects import CategoryName
from app.domain.transaction.transaction_value_objects import TransactionType


class CategoryDTO(Base):
    """Data Transfer Object for Category entity"""

    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(nullable=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False, default="")
    type: Mapped[str] = mapped_column(nullable=False)
    is_archived: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    def to_entity(self) -> "Category":
        """Convert DTO to Category entity."""
        return Category(
            name=CategoryName(self.name),
            type=TransactionType(self.type),
            id=self.id,
            user_id=self.user_id,
            description=self.description,
            is_archived=self.is_archived,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_entity(category: "Category") -> "CategoryDTO":
        """Create DTO from Category entity."""
        return CategoryDTO(
            id=category.id,
            user_id=category.user_id,
            name=category.name.value,
            description=category.description,
            type=category.type.value,
            is_archived=category.is_archived,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
