from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.transaction.transaction_repository import TransactionRepository
from app.infrastructure.transaction.repo import (
    new_transaction_repository,
)
from app.usecase.transaction.create_transaction_usecase import (
    CreateTransactionUseCase,
    new_create_transaction_usecase,
)
from app.usecase.transaction.get_transactions_usecase import (
    GetTransactionsUseCase,
    new_get_transactions_usecase,
)


def get_transaction_repository(session: Session = Depends(get_db)) -> TransactionRepository:
    return new_transaction_repository(session)


def get_create_transaction_usecase(
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
) -> CreateTransactionUseCase:
    return new_create_transaction_usecase(transaction_repo)


def get_get_transactions_usecase(
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
) -> GetTransactionsUseCase:
    return new_get_transactions_usecase(transaction_repo)
