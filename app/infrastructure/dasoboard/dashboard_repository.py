from requests import Session
from sqlalchemy import func, select

from app.domain.dashboard.dashboard_entity import DashboardCategoryBreakdown, DashboardSummary
from app.domain.dashboard.dashboard_repository import DashboardSuammaryRepository
from app.domain.transaction.transaction_value_objects import CategorySummary, TransactionType
from app.infrastructure.category.category_dto import CategoryDTO
from app.infrastructure.transaction.transaction_dto import TransactionDTO


class DashboardSuammaryRepositoryImpl(DashboardSuammaryRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_expense_total(self, user_id, from_, to) -> int:
        stmt = (
            select(func.coalesce(func.sum(TransactionDTO.amount), 0))
            .where(TransactionDTO.user_id == user_id)
            .where(TransactionDTO.occurred_at.between(from_, to))
            .where(TransactionDTO.type == TransactionType.EXPENSE.value)
        )
        return self.db.execute(stmt).scalar_one()

    def get_income_total(self, user_id, from_, to) -> int:
        stmt = (
            select(func.coalesce(func.sum(TransactionDTO.amount), 0))
            .where(TransactionDTO.user_id == user_id)
            .where(TransactionDTO.occurred_at.between(from_, to))
            .where(TransactionDTO.type == TransactionType.INCOME.value)
        )
        return self.db.execute(stmt).scalar_one()

    def get_category_breakdown(self, user_id, from_, to) -> list[DashboardCategoryBreakdown]:
        stmt = (
            select(
                TransactionDTO.category_id,
                CategoryDTO.name,
                func.coalesce(func.sum(TransactionDTO.amount), 0).label("amount"),
            )
            .join(CategoryDTO, CategoryDTO.id == TransactionDTO.category_id)
            .where(TransactionDTO.user_id == user_id)
            .where(TransactionDTO.occurred_at.between(from_, to))
            .where(TransactionDTO.type == TransactionType.EXPENSE.value)
            .group_by(TransactionDTO.category_id, CategoryDTO.name)
        )
        rows = self.db.execute(stmt).all()

        total_expense = sum(row.amount for row in rows) or 0
        if total_expense == 0:
            return []

        breakdowns: list[DashboardCategoryBreakdown] = []
        for row in rows:
            category = CategorySummary(id=row.category_id, name=row.name)
            ratio = float(row.amount) / float(total_expense)
            breakdowns.append(
                DashboardCategoryBreakdown(category=category, amount=row.amount, ratio=ratio)
            )
        return breakdowns


def new_dashboard_summary_repository(session: Session) -> DashboardSuammaryRepository:
    return DashboardSuammaryRepositoryImpl(session)
