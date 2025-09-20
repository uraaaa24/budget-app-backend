from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date
from uuid import UUID

from app.domain.transaction.transaction_entity import Transaction


class TransactionRepository(ABC):
    """Repository interface for Transaction entities."""

    @abstractmethod
    def add(self, entity: Transaction) -> None: ...

    @abstractmethod
    def update(self, entity: Transaction) -> None: ...

    @abstractmethod
    def find_by_id(self, entity_id: UUID) -> Transaction | None: ...

    @abstractmethod
    def find_all(self) -> list[Transaction]: ...

    @abstractmethod
    def remove(self, entity_id: UUID) -> None: ...

    @abstractmethod
    def find_by_account_and_period(
        self, account_id: UUID, start: date, end: date
    ) -> Iterable[Transaction]: ...

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[Transaction]: ...
