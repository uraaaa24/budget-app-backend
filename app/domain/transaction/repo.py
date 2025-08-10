# domain/transactions/repositories/transaction_repository.py
from abc import abstractmethod
from datetime import date
from typing import Iterable
from uuid import UUID

from app.domain.base_repo import BaseRepository
from app.domain.transaction.transaction import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    """Repository interface for Transaction entities."""

    @abstractmethod
    def find_by_account_and_period(
        self, account_id: UUID, start: date, end: date
    ) -> Iterable[Transaction]: ...

    @abstractmethod
    def find_by_user_id(self, user_id: UUID) -> list[Transaction]: ...
