from fastapi import APIRouter, Depends, HTTPException, logger, status
from pydantic import ValidationError

from app.core.auth import get_current_user
from app.infrastructure.di.injection import (
    get_create_transaction_usecase,
    get_delete_transaction_usecase,
    get_get_transactions_usecase,
    get_put_transaction_usecase,
)
from app.presentation.schemas.requests.transaction import (
    CreateTransactionRequestSchema,
    UpdateTransactionRequestSchema,
)
from app.presentation.schemas.responses.transaction import (
    CreateTransactionResponseSchema,
    GetTransactionListResponseSchema,
    UpdateTransactionResponseSchema,
)
from app.usecase.transaction.create_transaction_usecase import CreateTransactionUseCase
from app.usecase.transaction.delete_transaction_usecase import DeleteTransactionUseCase
from app.usecase.transaction.get_transactions_usecase import GetTransactionsUseCase
from app.usecase.transaction.put_transaction_usecase import PutTransactionUseCase

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


@router.put(
    "/transactions/{transaction_id}",
    response_model=UpdateTransactionResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_400_BAD_REQUEST: {"description": "Bad Request"}},
)
async def update_transaction(
    transaction_id: str,
    data: UpdateTransactionRequestSchema,
    auth_context=Depends(get_current_user),
    usecase: PutTransactionUseCase = Depends(get_put_transaction_usecase),
):
    """Update a transaction by ID for the current user"""
    try:
        update_data = data.model_dump()
        result = usecase.execute(auth_context.sub, transaction_id, update_data)
        return UpdateTransactionResponseSchema.from_entity(result)
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


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    _auth_context=Depends(get_current_user),
    usecase: DeleteTransactionUseCase = Depends(get_delete_transaction_usecase),
):
    """Delete a transaction by ID for the current user"""
    usecase.execute(transaction_id)
    return {"message": "Transaction deleted successfully"}
