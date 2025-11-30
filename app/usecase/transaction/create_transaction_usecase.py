from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.transaction.transaction_entity import Transaction
from app.domain.transaction.transaction_repository import TransactionRepository
from app.domain.transaction.transaction_value_objects import TransactionType


class CreateTransactionUseCase(ABC):
    @abstractmethod
    def execute(self, user_id: str, data: dict[str, Any]) -> Transaction: ...


class CreateTransactionUseCaseImpl(CreateTransactionUseCase):
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def execute(self, user_id: str, data: dict[str, Any]) -> Transaction:
        occurred_at = data["occurred_at"]
        if isinstance(occurred_at, datetime):
            occurred_at = occurred_at.date()

        category_id = data.get("category_id")
        if category_id is not None and category_id not in ("", "null"):
            category_id = category_id if isinstance(category_id, UUID) else UUID(str(category_id))
        else:
            category_id = None

        transaction = Transaction.create(
            user_id=user_id,
            account_id=None,
            type=TransactionType(data["type"]),
            amount=data["amount"],
            occurred_at=occurred_at,
            category_id=category_id,
            description=data.get("description", ""),
        )

        self.transaction_repo.add(transaction)
        return transaction


def new_create_transaction_usecase(
    transaction_repo: TransactionRepository,
) -> CreateTransactionUseCase:
    return CreateTransactionUseCaseImpl(transaction_repo)
