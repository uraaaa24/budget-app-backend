from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_user
from app.infrastructure.di.injection import get_dashboard_summary_usecase
from app.presentation.schemas.responses.dasuboard import GetDashboardSummaryResponseSchema
from app.usecase.dashboard.get_dashboard_summary_usecase import GetDashboardSummaryUseCase

router = APIRouter(tags=["dashboard"])


@router.get(
    "/dashboard/summary",
    response_model=GetDashboardSummaryResponseSchema,
    status_code=status.HTTP_200_OK,
)
def get_dashboard_summary(
    auth_context=Depends(get_current_user),
    usecase: GetDashboardSummaryUseCase = Depends(get_dashboard_summary_usecase),
    from_: date | None = Query(None, alias="from"),
    to: date | None = Query(None, alias="to"),
):
    """Retrieve dashboard summary data"""
    print("🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥")

    try:
        today = date.today()
        if to is None:
            to = today
        if from_ is None:
            from_ = to.replace(day=1)

        dashboard_summary = usecase.execute(auth_context.sub, from_, to)
        return GetDashboardSummaryResponseSchema.from_entity(dashboard_summary)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
