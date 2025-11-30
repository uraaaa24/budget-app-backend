from datetime import date

from pydantic import BaseModel, Field

from app.domain.dashboard.dashboard_entity import DashboardSummary


class DashboardPeriodSchema(BaseModel):
    from_: date = Field(..., alias="from", description="Start date of the period")
    to: date = Field(..., description="End date of the period")


class DashboardTotalSchema(BaseModel):
    expense: int = Field(..., description="Total expenses")
    income: int = Field(..., description="Total income")
    net: int = Field(..., description="Net amount")
    average_daily_expense: float = Field(..., description="Average daily expense")


class DashboardCategorySummarySchema(BaseModel):
    category_id: str = Field(..., description="Unique identifier of the category")
    category_name: str = Field(..., description="Name of the category")
    total_amount: int = Field(..., description="Total amount for the category")
    ratio: float = Field(..., description="Ratio of the category to total expenses")


class GetDashboardSummaryResponseSchema(BaseModel):
    """Schema for dashboard summary response."""

    period: DashboardPeriodSchema = Field(..., description="Period of the dashboard summary")
    total: DashboardTotalSchema = Field(..., description="Total amounts summary")
    by_category: list[DashboardCategorySummarySchema] = Field(
        ..., description="List of category summaries"
    )

    @staticmethod
    def from_entity(entity: "DashboardSummary") -> "GetDashboardSummaryResponseSchema":
        """Convert a DashboardSummary entity to schema."""
        return GetDashboardSummaryResponseSchema(
            period=DashboardPeriodSchema(**{"from": entity.period.from_, "to": entity.period.to}),
            total=DashboardTotalSchema(
                expense=entity.total.expense,
                income=entity.total.income,
                net=entity.total.net,
                average_daily_expense=entity.total.averate_daily_expense,
            ),
            by_category=[
                DashboardCategorySummarySchema(
                    category_id=str(cb.category.id),
                    category_name=cb.category.name,
                    total_amount=cb.amount,
                    ratio=cb.ratio,
                )
                for cb in entity.by_category
            ],
        )
