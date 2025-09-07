from fastapi import APIRouter, Depends, status

from app.core.auth import get_current_user
from app.infrastructure.di.injection import (
    get_create_transaction_usecase,
    get_get_transactions_usecase,
)
from app.presentation.schemas.requests.transaction import CreateTransactionRequestSchema
from app.presentation.schemas.responses.transaction import (
    CreateTransactionResponseSchema,
    GetTransactionResponseSchema,
    GetTransactionsResponseSchema,
)
from app.usecase.transaction.create_transaction_usecase import CreateTransactionUseCase
from app.usecase.transaction.get_transactions_usecase import GetTransactionsUseCase

router = APIRouter(tags=["transaction"])


@router.get("/transactions", response_model=GetTransactionsResponseSchema)
async def get_transactions(
    auth_context=Depends(get_current_user),
    usecase: GetTransactionsUseCase = Depends(get_get_transactions_usecase),
):
    """Retrieve transactions for the current user"""
    transactions = usecase.execute(auth_context.sub)

    transaction_responses = []
    for transaction in transactions:
        transaction_responses.append(
            GetTransactionResponseSchema(
                id=transaction.id,
                account_id=transaction.account_id,
                type=str(transaction.type.value),
                amount=transaction.amount.value,
                occurred_at=transaction.occurred_at,
                category_id=transaction.category_id,
                description=transaction.description,
                created_at=transaction.created_at,
                updated_at=transaction.updated_at,
            )
        )

    return GetTransactionsResponseSchema(transactions=transaction_responses)


@router.post(
    "/transactions",
    response_model=CreateTransactionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    data: CreateTransactionRequestSchema,
    auth_context=Depends(get_current_user),
    usecase: CreateTransactionUseCase = Depends(get_create_transaction_usecase),
):
    """Create a new transaction for the current user"""
    try:
        print(f"DEBUG: Parsed data: {data}")  # Debug parsed data

        # Convert Pydantic model to dict for UseCase
        transaction_data = {
            # "account_id": str(data.account_id),
            "type": data.type,
            "amount": data.amount,
            "occurred_at": data.occurred_at.isoformat()
            if hasattr(data.occurred_at, "isoformat")
            else str(data.occurred_at),
            # "category_id": str(data.category_id) if data.category_id else None,
            "description": data.description,
        }

        result = usecase.execute(auth_context.sub, transaction_data)

        return CreateTransactionResponseSchema(transaction_id=result)
    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        raise
