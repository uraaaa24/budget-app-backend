from abc import abstractmethod


class CreateTransactionUseCase:
    @abstractmethod
    def execute(self, user_id, dara: dict) -> str:
        pass


class CreateTransactionUseCaseImpl(CreateTransactionUseCase):
    def __init__(self, transaction_repo):
        self.transaction_repo = transaction_repo

    def execute(self, user_id, data: dict) -> str:
        transaction = self.transaction_repo.create_transaction(user_id, data)
        return str(transaction.id)
