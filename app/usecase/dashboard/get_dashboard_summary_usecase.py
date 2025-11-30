from abc import abstractmethod
from datetime import date

from app.domain.dashboard.dashboard_entity import DashboardPeriod, DashboardSummary, DashboardTotal
from app.domain.dashboard.dashboard_repository import DashboardSuammaryRepository


class GetDashboardSummaryUseCase:
    @abstractmethod
    def execute(self, user_id) -> DashboardSummary:
        pass


class GetDashboardSummaryUseCaseImpl(GetDashboardSummaryUseCase):
    def __init__(self, dashboard_repo: DashboardSuammaryRepository):
        self.dashboard_repo = dashboard_repo

    def execute(self, user_id: str, from_: date, to: date) -> DashboardSummary:
        expense = self.dashboard_repo.get_expense_total(user_id, from_, to)
        income = self.dashboard_repo.get_income_total(user_id, from_, to)
        net = income - expense

        days = (to - from_).days + 1
        avg_daily = float(expense) / days if days > 0 else 0.0

        period = DashboardPeriod(from_=from_, to=to)
        total = DashboardTotal(
            expense=expense, income=income, net=net, averate_daily_expense=avg_daily
        )
        by_category = self.dashboard_repo.get_category_breakdown(user_id, from_, to)

        return DashboardSummary(period=period, total=total, by_category=by_category)


def new_get_dashboard_summary_usecase(
    dashboard_repo: DashboardSuammaryRepository,
) -> GetDashboardSummaryUseCase:
    return GetDashboardSummaryUseCaseImpl(dashboard_repo)
