from doctest import debug

from fastapi import APIRouter, Depends, HTTPException, logger, status
from pydantic import ValidationError

from app.core.auth import get_current_user
from app.infrastructure.di.injection import (
    get_create_transaction_usecase,
    get_delete_transaction_usecase,
    get_get_transactions_usecase,
    get_put_transaction_usecase,
)
from app.presentation.schemas.requests.transaction import CreateTransactionRequestSchema
from app.presentation.schemas.responses.transaction import (
    CreateTransactionResponseSchema,
    GetTransactionListResponseSchema,
)
from app.usecase.transaction.create_transaction_usecase import CreateTransactionUseCase
from app.usecase.transaction.delete_transaction_usecase import DeleteTransactionUseCase
from app.usecase.transaction.get_transactions_usecase import GetTransactionsUseCase
from app.usecase.transaction.put_tranaction_usecase import PutTransactionUseCase

router = APIRouter(tags=["transaction"])


@router.get(
    "/transactions", response_model=GetTransactionListResponseSchema, status_code=status.HTTP_200_OK
)
async def get_transactions(
    auth_context=Depends(get_current_user),
    usecase: GetTransactionsUseCase = Depends(get_get_transactions_usecase),
):
    """Retrieve transactions for the current user"""
    try:
        transactions = usecase.execute(auth_context.sub)
        return GetTransactionListResponseSchema.from_entities(transactions)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from e


@router.post(
    "/transactions",
    response_model=CreateTransactionResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad Request"},
    },
)
async def create_transaction(
    data: CreateTransactionRequestSchema,
    auth_context=Depends(get_current_user),
    usecase: CreateTransactionUseCase = Depends(get_create_transaction_usecase),
):
    """Create a new transaction for the current user"""
    try:
        transaction_data = data.model_dump()
        result = usecase.execute(auth_context.sub, transaction_data)
        return CreateTransactionResponseSchema.from_entity(result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except ValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors()
        ) from ve
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from e

    # try:
    #     print(f"DEBUG: Parsed data: {data}")  # Debug parsed data

    #     # Convert Pydantic model to dict for UseCase
    #     transaction_data = {
    #         # "account_id": str(data.account_id),
    #         "type": data.type,
    #         "amount": data.amount,
    #         "occurred_at": data.occurred_at.isoformat()
    #         if hasattr(data.occurred_at, "isoformat")
    #         else str(data.occurred_at),
    #         # "category_id": str(data.category_id) if data.category_id else None,
    #         "description": data.description,
    #     }

    #     result = usecase.execute(auth_context.sub, transaction_data)

    #     return CreateTransactionResponseSchema(transaction_id=result)
    # except Exception as e:
    #     print(f"DEBUG: Exception occurred: {e}")
    #     raise


@router.put("/transactions/{transaction_id}", status_code=status.HTTP_200_OK)
async def update_transaction(
    transaction_id: str,
    data: CreateTransactionRequestSchema = None,
    _auth_context=Depends(get_current_user),
    usecase: PutTransactionUseCase = Depends(get_put_transaction_usecase),
):
    """Update a transaction by ID for the current user"""
    update_data = data.model_dump()
    usecase.execute(transaction_id, update_data)
    return {"message": "Transaction updated successfully"}


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    _auth_context=Depends(get_current_user),
    usecase: DeleteTransactionUseCase = Depends(get_delete_transaction_usecase),
):
    """Delete a transaction by ID for the current user"""
    usecase.execute(transaction_id)
    return {"message": "Transaction deleted successfully"}
