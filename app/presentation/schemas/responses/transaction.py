from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.transaction.transaction_entity import Transaction


class CreateTransactionResponseSchema(BaseModel):
    """Schema for transaction creation response."""

    transaction_id: UUID = Field(..., description="Unique identifier of the created transaction")


class GetTransactionResponseSchema(BaseModel):
    """Schema for individual transaction in response."""

    id: UUID = Field(..., description="Unique identifier of the transaction")
    account_id: UUID | None = Field(
        None, description="Account ID associated with the transaction (optional)"
    )
    type: str = Field(..., description="Type of transaction (income or expense)")
    amount: int = Field(..., description="Amount of the transaction")
    occurred_at: date = Field(..., description="Date when the transaction occurred")
    category_id: UUID | None = Field(None, description="Category ID (optional)")
    description: str = Field("", description="Description of the transaction")
    created_at: datetime = Field(..., description="Timestamp when the transaction was created")
    updated_at: datetime = Field(..., description="Timestamp when the transaction was last updated")

    @staticmethod
    def from_entity(entity: Transaction) -> "GetTransactionResponseSchema":
        """Convert a Transaction entity to response schema."""
        return GetTransactionResponseSchema(
            id=entity.id,
            account_id=entity.account_id,
            type=str(entity.type.value),
            amount=entity.amount.value,
            occurred_at=entity.occurred_at,
            category_id=entity.category_id,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class GetTransactionListResponseSchema(BaseModel):
    """Schema for list of transactions in response."""

    transactions: list[GetTransactionResponseSchema] = Field(
        ..., description="List of transactions"
    )

    @staticmethod
    def from_entities(entities: list[Transaction]) -> "GetTransactionListResponseSchema":
        """Convert a list of Transaction entities to response schema."""
        return GetTransactionListResponseSchema(
            transactions=[GetTransactionResponseSchema.from_entity(e) for e in entities]
        )
