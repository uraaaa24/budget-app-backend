from abc import abstractmethod

from app.domain.category.category_entity import Category
from app.domain.category.category_repository import CategoryRepository


class GetCategoryListUseCase:
    @abstractmethod
    def execute(self, user_id: str) -> list[Category]:
        pass


class GetCategoryListUseCaseImpl(GetCategoryListUseCase):
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def execute(self, user_id: str) -> list[Category]:
        categories = self.category_repo.find_all_accessible_by_user(user_id)
        return sorted(categories, key=lambda c: c.created_at, reverse=True)


def new_get_category_list_usecase(
    category_repo: CategoryRepository,
) -> GetCategoryListUseCase:
    return GetCategoryListUseCaseImpl(category_repo)
