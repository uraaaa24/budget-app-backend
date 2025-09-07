from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class CreateTransactionRequestSchema(BaseModel):
    """Schema for creating a new transaction."""

    # account_id: UUID = Field(..., description="Account ID for the transaction")
    type: str = Field(
        ..., pattern="^(income|expense)$", description="Transaction type: income or expense"
    )
    amount: int = Field(..., gt=0, description="Transaction amount in cents, must be positive")
    occurred_at: datetime = Field(..., description="Date when the transaction occurred")
    # category_id: UUID | None = Field(None, description="Optional category ID")
    description: str = Field("", max_length=255, description="Optional transaction description")

    @field_validator('occurred_at')
    @classmethod
    def convert_datetime_to_date(cls, v):
        """Convert datetime to date for storage"""
        if isinstance(v, datetime):
            return v.date()
        return v
