from abc import abstractmethod

from app.domain.transaction.transaction_repository import TransactionRepository


class PutTransactionUseCase:
    @abstractmethod
    def execute(self, user_id: str, transaction_id: str, data: dict):
        pass


class PutTransactionUseCaseImpl(PutTransactionUseCase):
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def execute(self, transaction_id: str, data: dict):
        # Fetch the existing transaction
        transaction = self.transaction_repo.find_by_id(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")

        # Update the transaction fields
        for key, value in data.items():
            setattr(transaction, key, value)

        # Save the updated transaction
        self.transaction_repo.update(transaction)
        return transaction


def new_put_transaction_usecase(
    transaction_repo: TransactionRepository,
) -> PutTransactionUseCase:
    return PutTransactionUseCaseImpl(transaction_repo)
