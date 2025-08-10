from dataclasses import dataclass
from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.transaction.transaction import Transaction
from app.domain.transaction.vo import Amount, TransactionType
from app.infrastructure.transaction.repo import TransactionRepositoryImpl


@dataclass(frozen=True)
class CreateTransactionInput:
    """Data Transfer Object for creating a transaction."""

    user_id: UUID
    account_id: UUID
    type: str
    amount: int
    occurred_at: date
    category_id: UUID | None = None
    description: str = ""


@dataclass(frozen=True)
class UpdateTransactionInput:
    """Data Transfer Object for updating a transaction."""

    type: str | None = None
    amount: int | None = None
    occurred_at: date | None = None
    category_id: UUID | None = None
    description: str | None = None


def create_transaction(session: Session, data: CreateTransactionInput) -> UUID:
    """Create a new transaction in the database."""

    repo = TransactionRepositoryImpl(session)

    transaction = Transaction.create(
        user_id=data.user_id,
        account_id=data.account_id,
        type=TransactionType(data.type),
        amount=data.amount,
        occurred_at=data.occurred_at,
        category_id=data.category_id,
        description=data.description,
    )

    repo.add(transaction)
    return transaction.id


def update_transaction(
    session: Session, transaction_id: UUID, data: UpdateTransactionInput
) -> None:
    """Update an existing transaction in the database."""

    repo = TransactionRepositoryImpl(session)
    current_transaction = repo.find_by_id(transaction_id)

    if not current_transaction:
        raise KeyError(f"Transaction not found: {transaction_id}")
    new_transaction = Transaction(
        id=current_transaction.id,
        user_id=current_transaction.user_id,
        account_id=current_transaction.account_id,
        type=TransactionType(data.type) if data.type else current_transaction.type,
        amount=Amount(data.amount) if data.amount else current_transaction.amount,
        occurred_at=data.occurred_at or current_transaction.occurred_at,
        category_id=data.category_id or current_transaction.category_id,
        description=data.description or current_transaction.description,
        created_at=current_transaction.created_at,
        updated_at=current_transaction.updated_at,
    )
    repo.update(new_transaction)
    return


def get_user_transactions(session: Session, user_id: UUID) -> list[Transaction]:
    """Retrieve transactions for a specific user from the database."""

    repo = TransactionRepositoryImpl(session)
    return repo.find_by_user_id(user_id)
