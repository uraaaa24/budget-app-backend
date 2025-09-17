from collections.abc import Iterable
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.transaction.transaction import Transaction
from app.domain.transaction.transaction_repository import TransactionRepository
from app.infrastructure.transaction.dto import TransactionDTO


class TransactionRepositoryImpl(TransactionRepository):
    """SQLAlchemy implementation of TransactionRepository."""

    def __init__(self, session: Session) -> None:
        """Initialize with a SQLAlchemy session."""
        self.session = session

    def find_all(self) -> list[Transaction]:
        """Retrieve all transactions."""
        rows = self.session.execute(select(TransactionDTO)).scalars().all()
        return [row.to_entity() for row in rows]

    def find_by_user_id(self, user_id: str) -> list[Transaction]:
        """Retrieve transactions by user ID."""
        rows = (
            self.session.execute(select(TransactionDTO).where(TransactionDTO.user_id == user_id))
            .scalars()
            .all()
        )
        return [row.to_entity() for row in rows]

    def add(self, entity: Transaction) -> None:
        """Add a new transaction."""
        if self.session.get(TransactionDTO, entity.id) is not None:
            raise KeyError(f"Transaction already exists: {entity.id}")

        self.session.add(TransactionDTO.from_entity(entity))

    def update(self, entity: Transaction) -> None:
        """Update an existing transaction."""
        row = self.session.get(TransactionDTO, entity.id)
        if row is None:
            raise KeyError(f"Transaction not found: {entity.id}")

        row.user_id = entity.user_id
        row.account_id = entity.account_id
        row.type = entity.type
        row.amount = entity.amount
        row.occurred_at = entity.occurred_at
        row.category_id = entity.category_id
        row.description = entity.description
        row.created_at = entity.created_at
        row.updated_at = entity.updated_at

    def find_by_id(self, entity_id: UUID) -> Transaction | None:
        """Find transaction by ID."""
        row = self.session.get(TransactionDTO, entity_id)
        return row.to_entity() if row else None

    def remove(self, entity_id: UUID) -> None:
        """Remove transaction by ID."""
        row = self.session.get(TransactionDTO, entity_id)
        if row is None:
            raise KeyError(f"Transaction not found: {entity_id}")
        self.session.delete(row)

    def find_by_account_and_period(
        self, account_id: UUID, start: date, end: date
    ) -> Iterable[Transaction]:
        """Find transactions by account and period."""
        rows = (
            self.session.execute(
                select(TransactionDTO)
                .where(TransactionDTO.account_id == account_id)
                .where(TransactionDTO.occurred_at >= start)
                .where(TransactionDTO.occurred_at <= end)
            )
            .scalars()
            .all()
        )
        return [row.to_entity() for row in rows]


def new_transaction_repository(session: Session) -> TransactionRepository:
    return TransactionRepositoryImpl(session)
