from fastapi import APIRouter, Depends, status

from app.core.auth import get_current_user
from app.infrastructure.di.injection import get_create_transaction_usecase
from app.presentation.schemas.requests.transaction import CreateTransactionRequestSchema
from app.presentation.schemas.responses.transaction import CreateTransactionResponseSchema
from app.usecase.transaction.create_transaction_usecase import CreateTransactionUseCase

router = APIRouter(tags=["transaction"])


@router.get("/transactions")
async def get_transactions(user_id: str = Depends(get_current_user)):
    """Retrieve transactions for the current user"""
    # Placeholder for actual transaction retrieval logic
    return {"message": f"Transactions for user {user_id}"}


@router.post(
    "/transactions",
    response_model=CreateTransactionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    data: CreateTransactionRequestSchema,
    user_id: str = Depends(get_current_user),
    usecase: CreateTransactionUseCase = Depends(get_create_transaction_usecase),
):
    """Create a new transaction for the current user"""
    result = usecase.execute(user_id, data.model_dump())
    return {"transaction_id": result}
