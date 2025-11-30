from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.domain.transaction.transaction_entity import Transaction
from app.domain.transaction.transaction_repository import TransactionRepository
from app.domain.transaction.transaction_value_objects import Amount, TransactionType


class PutTransactionUseCase(ABC):
    @abstractmethod
    def execute(self, user_id: str, transaction_id: str, data: dict[str, Any]) -> Transaction: ...


class PutTransactionUseCaseImpl(PutTransactionUseCase):
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def execute(self, user_id: str, transaction_id: str, data: dict[str, Any]) -> Transaction:
        try:
            tx_id = UUID(transaction_id)
        except ValueError as e:
            raise ValueError("Invalid transaction_id") from e

        transaction = self.transaction_repo.find_by_id(tx_id)
        if not transaction:
            raise ValueError("Transaction not found")

        if transaction.user_id != user_id:
            raise ValueError("Access denied: Transaction does not belong to current user")

        if "type" in data:
            transaction.type = TransactionType(data["type"])

        if "amount" in data:
            transaction.amount = Amount(int(data["amount"]))

        if "occurred_at" in data:
            occurred_at = data["occurred_at"]
            transaction.occurred_at = (
                occurred_at.date() if isinstance(occurred_at, datetime) else occurred_at
            )

        if "description" in data:
            transaction.description = data["description"] or ""

        if "category_id" in data:
            category_id = data["category_id"]
            if category_id is None or category_id in ("", "null"):
                transaction.category = None
            else:
                uuid_id = category_id if isinstance(category_id, UUID) else UUID(str(category_id))
                transaction.change_category(uuid_id)

        transaction.updated_at = datetime.now(UTC)
        self.transaction_repo.update(transaction)
        return transaction


def new_put_transaction_usecase(transaction_repo: TransactionRepository) -> PutTransactionUseCase:
    return PutTransactionUseCaseImpl(transaction_repo)
