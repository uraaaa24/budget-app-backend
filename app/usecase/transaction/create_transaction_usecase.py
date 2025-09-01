from abc import abstractmethod

from app.domain.transaction.transaction import Transaction
from app.domain.transaction.transaction_repository import TransactionRepository


class CreateTransactionUseCase:
    @abstractmethod
    def execute(self, user_id, dara: dict) -> str:
        pass


class CreateTransactionUseCaseImpl(CreateTransactionUseCase):
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def execute(self, user_id, data: dict) -> Transaction:
        transaction = self.transaction_repo.create_transaction(user_id, data)
        return str(transaction.id)


def new_create_transaction_usecase(
    transaction_repo: TransactionRepository,
) -> CreateTransactionUseCase:
    return CreateTransactionUseCaseImpl(transaction_repo)
