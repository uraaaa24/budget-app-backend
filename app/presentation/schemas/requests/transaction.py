from pydantic import BaseModel


class CreateTransactionSchema(BaseModel):
    """Schema for creating a new transaction."""

    account_id: str
    type: str
    amount: int
    occurred_at: str  # ISO 8601 date string
    category_id: str | None = None
    description: str = ""
