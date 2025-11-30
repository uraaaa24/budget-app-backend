from datetime import UTC, date, datetime, timezone
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

JST = ZoneInfo("Asia/Tokyo")


class CreateTransactionRequestSchema(BaseModel):
    """Schema for creating a new transaction."""

    model_config = ConfigDict(extra="forbid")

    # account_id: UUID = Field(..., description="Account ID for the transaction")
    type: Literal["income", "expense"] = Field(
        ..., description="Transaction type: income or expense"
    )

    amount: int = Field(..., gt=0, description="Transaction amount in cents, must be positive")

    occurred_at: datetime = Field(..., description="Date when the transaction occurred")

    category_id: UUID | None = Field(None, description="Optional category ID")

    description: str = Field("", max_length=255, description="Optional transaction description")

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        return v.strip().lower() if isinstance(v, str) else v

    @field_validator("occurred_at", mode="before")
    @classmethod
    def parse_to_datetime(cls, v):
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            return datetime.fromisoformat(s)
        from datetime import time

        if isinstance(v, date):
            return datetime.combine(v, time(0, 0))
        raise TypeError("occurred_at must be ISO datetime or date")

    @field_validator("category_id", mode="before")
    @classmethod
    def empty_uuid_to_none(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator("description", mode="before")
    @classmethod
    def normalize_desc(cls, v):
        if v is None:
            return ""
        if isinstance(v, str):
            s = v.strip()
            return s if s else ""
        return v

    @field_validator("occurred_at")
    @classmethod
    def no_future_date(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            v_local = v.replace(tzinfo=JST)
        else:
            v_local = v.astimezone(JST)

        occurred_date = v_local.date()
        today_local = datetime.now(JST).date()

        if occurred_date > today_local:
            raise ValueError("occurred_at cannot be in the future")
        return v


class UpdateTransactionRequestSchema(CreateTransactionRequestSchema):
    """Schema for updating an existing transaction."""
