from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user
from app.infrastructure.di.injection import get_get_category_list_usecase
from app.presentation.schemas.responses.category import GetCategoryListResponseSchema
from app.usecase.category.get_categories import (
    GetCategoryListUseCase,
)

router = APIRouter(tags=["category"])


@router.get(
    "/categories", response_model=GetCategoryListResponseSchema, status_code=status.HTTP_200_OK
)
async def get_categories(
    auth_context=Depends(get_current_user),
    usecase: GetCategoryListUseCase = Depends(get_get_category_list_usecase),
):
    """Retrieve categories for the current user"""
    try:
        categories = usecase.execute(auth_context.sub)
        return GetCategoryListResponseSchema.from_entities(categories)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from e
