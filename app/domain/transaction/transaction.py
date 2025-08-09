
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.domain.base_entity import BaseEntity
from app.domain.transaction.vo import Amount, TransactionType


@dataclass(eq=False, slots=True)
class Transaction(BaseEntity):
    """Entity representing a financial transaction."""
    
    account_id: UUID
    type: TransactionType
    amount: Amount
    occurred_at: date
    category_id: UUID | None = None
    description: str = ""
    
    @classmethod
    def create(
        cls,
        *,
        account_id: UUID,
        type: TransactionType,
        amount: int,
        occurred_at: date,
        category_id: UUID | None = None,
        description: str = "",
    ) -> "Transaction":
        """Factory method to create a new transaction."""
        return cls(
            account_id=account_id,
            type=type,
            amount=Amount(amount),
            occurred_at=occurred_at,
            category_id=category_id,
            description=description
        )
    
    def __post_init__(self):
        """Ensure that the amount is always non-negative."""
        super().__post_init__()
        
        if self.amount < 0:
            raise ValueError("Transaction amount cannot be negative.")

    @property
    def signed_amount(self) -> int:
        """Return the amount with a sign based on the transaction type."""
        base = self.amount.value
        return base if self.type.is_income else -base
    