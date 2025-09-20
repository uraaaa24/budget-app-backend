from abc import abstractmethod
from datetime import date

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

    def execute(self, user_id: str, data: dict) -> str:
        transaction = Transaction.create(
            user_id=user_id,
            # account_id=UUID(data["account_id"]),
            account_id=None,  # Temporary: will be implemented later
            type=TransactionType(data["type"]),
            amount=data["amount"],
            occurred_at=date.fromisoformat(data["occurred_at"]),
            # category_id=UUID(data["category_id"]) if data.get("category_id") else None,
            category_id=None,  # Temporary: will be implemented later
            description=data.get("description", ""),
        )

        self.transaction_repo.add(transaction)
        return str(transaction.id)


def new_create_transaction_usecase(
    transaction_repo: TransactionRepository,
) -> CreateTransactionUseCase:
    return CreateTransactionUseCaseImpl(transaction_repo)
