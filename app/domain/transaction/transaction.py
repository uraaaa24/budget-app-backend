from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from app.domain.transaction.transaction_value_objects import Amount, TransactionType


@dataclass(eq=False, slots=True)
class Transaction:
    """Entity representing a financial transaction."""

    user_id: str
    # account_id: UUID
    account_id: UUID | None  # Temporary: will be implemented later
    type: TransactionType
    amount: Amount
    occurred_at: date
    id: UUID = field(default_factory=uuid4)
    category_id: UUID | None = None
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, Transaction):
            return self.id == obj.id
        return False

    def __hash__(self) -> int:
        return hash((type(self), self.id))

    @classmethod
    def create(
        cls,
        user_id: str,
        # account_id: UUID,
        account_id: UUID | None,  # Temporary: will be implemented later
        type: TransactionType,
        amount: int,
        occurred_at: date,
        category_id: UUID | None = None,
        description: str = "",
    ) -> "Transaction":
        """Factory method to create a new transaction."""
        return cls(
            user_id=user_id,
            account_id=account_id,
            type=type,
            amount=Amount(amount),
            occurred_at=occurred_at,
            category_id=category_id,
            description=description,
        )

    def __post_init__(self):
        """Ensure that the amount is always non-negative."""
        if self.amount.value < 0:
            raise ValueError("Transaction amount cannot be negative.")

    @property
    def signed_amount(self) -> int:
        """Return the amount with a sign based on the transaction type."""
        base = self.amount.value
        return base if self.type.is_income else -base
