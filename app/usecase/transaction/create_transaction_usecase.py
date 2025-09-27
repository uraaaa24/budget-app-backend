from abc import abstractmethod
from datetime import date
from uuid import UUID

from app.domain.transaction.transaction_entity import Transaction
from app.domain.transaction.transaction_repository import TransactionRepository
from app.domain.transaction.transaction_value_objects import TransactionType


class CreateTransactionUseCase:
    @abstractmethod
    def execute(self, user_id: str, data: dict) -> str:
        pass


class CreateTransactionUseCaseImpl(CreateTransactionUseCase):
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def execute(self, user_id: str, data: dict) -> Transaction:
        transaction = Transaction.create(
            user_id=user_id,
            # account_id=UUID(data["account_id"]),
            account_id=None,  # Temporary: will be implemented later
            type=TransactionType(data["type"]),
            amount=data["amount"],
            occurred_at=data["occurred_at"],
            category_id=UUID(data["category_id"]) if data.get("category_id") else None,
            description=data.get("description", ""),
        )

        self.transaction_repo.add(transaction)
        return Transaction(
            user_id=user_id,
            account_id=transaction.account_id,
            type=transaction.type,
            amount=transaction.amount,
            occurred_at=transaction.occurred_at,
            category_id=transaction.category_id,
            description=transaction.description,
            id=transaction.id,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
        )


def new_create_transaction_usecase(
    transaction_repo: TransactionRepository,
) -> CreateTransactionUseCase:
    return CreateTransactionUseCaseImpl(transaction_repo)
