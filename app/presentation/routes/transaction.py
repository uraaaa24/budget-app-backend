from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.presentation.schemas.requests.transaction import CreateTransactionSchema
from app.usecase.transaction.create_transaction_usecase import CreateTransactionUseCase

router = APIRouter(tags=["transaction"])


@router.get("/transactions")
async def get_transactions(user_id: str = Depends(get_current_user)):
    """Retrieve transactions for the current user"""
    # Placeholder for actual transaction retrieval logic
    return {"message": f"Transactions for user {user_id}"}


@router.post("/transactions")
async def create_transaction(
    data: CreateTransactionSchema, user_id: str = Depends(get_current_user)
):
    """Create a new transaction for the current user"""
    usecase = CreateTransactionUseCase()
