from abc import abstractmethod

from app.domain.transaction.transaction import Transaction
from app.domain.transaction.transaction_repository import TransactionRepository


class GetTransactionsUseCase:
    @abstractmethod
    def execute(self, user_id: str) -> list[Transaction]:
        pass


class GetTransactionsUseCaseImpl(GetTransactionsUseCase):
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def execute(self, user_id: str) -> list[Transaction]:
        return self.transaction_repo.find_by_user_id(user_id)


def new_get_transactions_usecase(
    transaction_repo: TransactionRepository,
) -> GetTransactionsUseCase:
    return GetTransactionsUseCaseImpl(transaction_repo)
