from abc import ABC, abstractmethod
from datetime import UTC, date, datetime
from uuid import UUID

from app.domain.transaction.transaction_repository import TransactionRepository
from app.domain.transaction.transaction_value_objects import Amount, TransactionType


class PutTransactionUseCase(ABC):
    @abstractmethod
    def execute(self, user_id: str, transaction_id: str, data: dict):
        pass


class PutTransactionUseCaseImpl(PutTransactionUseCase):
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def execute(self, user_id: str, transaction_id: str, data: dict):
        # Fetch the existing transaction
        transaction = self.transaction_repo.find_by_id(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")

        # Check if the transaction belongs to the current user
        if transaction.user_id != user_id:
            raise ValueError("Access denied: Transaction does not belong to current user")

        # Update the transaction fields (data is already validated by schema)
        updatable_fields = {
            "type": lambda v: TransactionType(v),
            "amount": lambda v: Amount(v),
            "occurred_at": lambda v: v.date() if isinstance(v, datetime) else v,
            "category_id": lambda v: v,
            "description": lambda v: v,
        }

        for key, value in data.items():
            if key in updatable_fields:
                setattr(transaction, key, updatable_fields[key](value))

        # Update timestamp
        transaction.updated_at = datetime.now(UTC)

        # Save the updated transaction
        self.transaction_repo.update(transaction)
        return transaction


def new_put_transaction_usecase(
    transaction_repo: TransactionRepository,
) -> PutTransactionUseCase:
    return PutTransactionUseCaseImpl(transaction_repo)
