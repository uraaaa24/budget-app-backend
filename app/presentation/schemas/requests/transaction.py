from datetime import UTC, date, datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CreateTransactionRequestSchema(BaseModel):
    """Schema for creating a new transaction."""

    model_config = ConfigDict(extra="forbid")  # 余計なキーは422

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
    def parse_to_date(cls, v):
        if isinstance(v, date) and not isinstance(v, datetime):
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            s = v.strip()
            try:
                return date.fromisoformat(s)  # "YYYY-MM-DD"
            except ValueError:
                if s.endswith("Z"):
                    s = s[:-1] + "+00:00"
                return datetime.fromisoformat(s).date()
        raise TypeError("occurred_at must be ISO date or ISO datetime")

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
        # 比較は日付同士に統一（UTC基準）
        today_utc = datetime.now(UTC).date()
        if v.tzinfo is None:
            occ_date = v.date()
        else:
            occ_date = v.astimezone(UTC).date()

        if occ_date > today_utc:
            raise ValueError("occurred_at cannot be in the future")
        return v
