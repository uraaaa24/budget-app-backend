from dataclasses import dataclass
from datetime import date

from app.domain.transaction.transaction_value_objects import CategorySummary


@dataclass(slots=True)
class DashboardPeriod:
    from_: date
    to: date


@dataclass(slots=True)
class DashboardTotal:
    expense: int
    income: int
    net: int
    averate_daily_expense: float


@dataclass(slots=True)
class DashboardCategoryBreakdown:
    category: CategorySummary
    amount: int
    ratio: float


@dataclass(slots=True)
class DashboardSummary:
    period: DashboardPeriod
    total: DashboardTotal
    by_category: list[DashboardCategoryBreakdown]
