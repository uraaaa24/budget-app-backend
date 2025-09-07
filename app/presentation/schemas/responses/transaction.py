from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateTransactionResponseSchema(BaseModel):
    """Schema for transaction creation response."""

    transaction_id: UUID = Field(..., description="Unique identifier of the created transaction")


class GetTransactionResponseSchema(BaseModel):
    """Schema for individual transaction in response."""

    id: UUID = Field(..., description="Unique identifier of the transaction")
    account_id: UUID | None = Field(None, description="Account ID associated with the transaction (optional)")
    type: str = Field(..., description="Type of transaction (income or expense)")
    amount: int = Field(..., description="Amount of the transaction")
    occurred_at: date = Field(..., description="Date when the transaction occurred")
    category_id: UUID | None = Field(None, description="Category ID (optional)")
    description: str = Field("", description="Description of the transaction")
    created_at: datetime = Field(..., description="Timestamp when the transaction was created")
    updated_at: datetime = Field(..., description="Timestamp when the transaction was last updated")


class GetTransactionsResponseSchema(BaseModel):
    """Schema for list of transactions response."""

    transactions: list[GetTransactionResponseSchema] = Field(..., description="List of transactions")
