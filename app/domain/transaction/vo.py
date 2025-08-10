from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class Amount:
    """Value object representing a monetary amount."""

    value: int

    def __post_init__(self):
        """Ensure the amount is non-negative."""
        if not isinstance(self.value, int):
            raise TypeError("Amount must be an integer.")
        if self.value < 0:
            raise ValueError("Amount must be a positive integer.")


class TransactionType(StrEnum):
    """Enumeration for transaction types."""

    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

    @property
    def is_income(self) -> bool:
        """Check if the transaction type is income."""
        return self == TransactionType.INCOME

    @property
    def is_expense(self) -> bool:
        """Check if the transaction type is expense."""
        return self == TransactionType.EXPENSE

    @property
    def is_transfer(self) -> bool:
        """Check if the transaction type is transfer."""
        return self == TransactionType.TRANSFER
