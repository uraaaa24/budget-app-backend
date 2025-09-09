from abc import abstractmethod
from uuid import UUID


class DeleteTransactionUseCase:
    @abstractmethod
    def execute(self, user_id: str, transaction_id: str) -> None:
        pass


class DeleteTransactionUseCaseImpl(DeleteTransactionUseCase):
    def __init__(self, transaction_repo):
        self.transaction_repo = transaction_repo

    def execute(self, transaction_id: str) -> None:
        self.transaction_repo.remove(UUID(transaction_id))


def new_delete_transaction_usecase(transaction_repo) -> DeleteTransactionUseCase:
    return DeleteTransactionUseCaseImpl(transaction_repo)
