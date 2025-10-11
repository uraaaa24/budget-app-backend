from abc import ABC, abstractmethod
from datetime import UTC, date, datetime
from uuid import UUID

from app.domain.transaction.transaction_entity import Transaction  # 型ヒント用(任意)
from app.domain.transaction.transaction_repository import TransactionRepository
from app.domain.transaction.transaction_value_objects import Amount, TransactionType


class PutTransactionUseCase(ABC):
    @abstractmethod
    def execute(self, user_id: str, transaction_id: str, data: dict) -> Transaction: ...


class PutTransactionUseCaseImpl(PutTransactionUseCase):
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def execute(self, user_id: str, transaction_id: str, data: dict) -> Transaction:
        # 1) IDをUUIDへ（Repository IFが UUID を期待しているため）
        try:
            tx_id = UUID(transaction_id)
        except Exception as e:
            raise ValueError("Invalid transaction_id") from e

        transaction = self.transaction_repo.find_by_id(tx_id)
        if not transaction:
            raise ValueError("Transaction not found")

        if transaction.user_id != user_id:
            raise ValueError("Access denied: Transaction does not belong to current user")

        def to_date(v: date | datetime) -> date:
            return v.date() if isinstance(v, datetime) else v

        updaters: dict[str, callable] = {
            "type": TransactionType,
            "amount": lambda v: Amount(int(v)),
            "occurred_at": to_date,
            "description": lambda v: v or "",
        }

        for field, conv in updaters.items():
            if field in data:
                setattr(transaction, field, conv(data[field]))

        if "category_id" in data:
            cid = data["category_id"]
            if cid in (None, "", "null"):
                transaction.category = None
            else:
                transaction.change_category(UUID(str(cid)))

        transaction.updated_at = datetime.now(UTC)

        self.transaction_repo.update(transaction)
        return transaction


def new_put_transaction_usecase(transaction_repo: TransactionRepository) -> PutTransactionUseCase:
    return PutTransactionUseCaseImpl(transaction_repo)
