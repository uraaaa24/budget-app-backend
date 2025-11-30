from abc import ABC, abstractmethod
from datetime import date

from app.domain.dashboard.dashboard_entity import DashboardCategoryBreakdown, DashboardSummary


class DashboardSuammaryRepository(ABC):
    @abstractmethod
    def get_expense_total(self, user_id: str, from_: date, to: date) -> int: ...

    @abstractmethod
    def get_income_total(self, user_id: str, from_: date, to: date) -> int: ...

    @abstractmethod
    def get_category_breakdown(
        self,
        user_id: str,
        from_: date,
        to: date,
    ) -> list[DashboardCategoryBreakdown]: ...
