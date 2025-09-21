from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.domain.category.category_repository import CategoryRepository
from app.infrastructure.category.category_dto import CategoryDTO


class CategoryRepositoryImpl(CategoryRepository):
    """In-memory implementation of CategoryRepository."""

    def __init__(self, session: Session) -> None:
        """Initialize with a SQLAlchemy session."""
        self.session = session

    def find_all_accessible_by_user(self, user_id: str) -> list:
        """Find all categories accessible by user (default categories + user-specific categories)."""
        rows = (
            self.session.execute(
                select(CategoryDTO).where(
                    or_(
                        CategoryDTO.user_id.is_(None),  # デフォルトカテゴリ
                        CategoryDTO.user_id == user_id  # ユーザー固有のカテゴリ
                    )
                )
            )
            .scalars()
            .all()
        )
        return [row.to_entity() for row in rows]

    def find_all_by_user_id(self, user_id: str) -> list:
        """Deprecated: Use find_all_accessible_by_user instead."""
        return self.find_all_accessible_by_user(user_id)

    def add(self, entity) -> None:
        """TODO: Implement when needed."""
        pass

    def update(self, entity) -> None:
        """TODO: Implement when needed."""
        pass

    def find_by_id_and_user_id(self, entity_id: str, user_id: str):
        """TODO: Implement when needed."""
        return None

    def remove(self, entity_id: str) -> None:
        """TODO: Implement when needed."""
        pass


def new_category_repository(session: Session) -> CategoryRepository:
    """Factory function to create a new CategoryRepository instance."""
    return CategoryRepositoryImpl(session)
