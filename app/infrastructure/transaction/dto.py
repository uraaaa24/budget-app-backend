from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domain.transaction.transaction import Transaction
from app.domain.transaction.transaction_value_objects import Amount, TransactionType


class TransactionDTO(Base):
    """Data Transfer Object for Transaction entity"""

    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), index=True, nullable=False)
    account_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(7), nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    occurred_at: Mapped[date] = mapped_column(nullable=False, index=True)
    category_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def to_entity(self) -> Transaction:
        """Convert DTO to Transaction entity."""
        return Transaction(
            id=self.id,
            user_id=self.user_id,
            account_id=self.account_id,
            type=TransactionType(self.type),
            amount=Amount(self.amount),
            occurred_at=self.occurred_at,
            category_id=self.category_id,
            description=self.description or "",
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_entity(transaction: Transaction) -> "TransactionDTO":
        """Create DTO from Transaction entity."""
        return TransactionDTO(
            id=transaction.id,
            user_id=transaction.user_id,
            account_id=transaction.account_id,
            type=transaction.type.value,
            amount=transaction.amount.value,
            occurred_at=transaction.occurred_at,
            category_id=transaction.category_id,
            description=transaction.description,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
        )
