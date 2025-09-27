from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.category.category_repository import CategoryRepository
from app.domain.transaction.transaction_repository import TransactionRepository
from app.infrastructure.category.category_repository import new_category_repository
from app.infrastructure.transaction.transaction_repository import (
    new_transaction_repository,
)
from app.usecase.category.get_categories import (
    GetCategoryListUseCase,
    new_get_category_list_usecase,
)
from app.usecase.transaction.create_transaction_usecase import (
    CreateTransactionUseCase,
    new_create_transaction_usecase,
)
from app.usecase.transaction.delete_transaction_usecase import (
    DeleteTransactionUseCase,
    new_delete_transaction_usecase,
)
from app.usecase.transaction.get_transactions_usecase import (
    GetTransactionsUseCase,
    new_get_transactions_usecase,
)
from app.usecase.transaction.put_transaction_usecase import (
    PutTransactionUseCase,
    new_put_transaction_usecase,
)


def get_transaction_repository(session: Session = Depends(get_db)) -> TransactionRepository:
    return new_transaction_repository(session)


def get_create_transaction_usecase(
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
) -> CreateTransactionUseCase:
    return new_create_transaction_usecase(transaction_repo)


def get_put_transaction_usecase(
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
) -> PutTransactionUseCase:
    return new_put_transaction_usecase(transaction_repo)


def get_get_transactions_usecase(
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
) -> GetTransactionsUseCase:
    return new_get_transactions_usecase(transaction_repo)


def get_delete_transaction_usecase(
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
) -> DeleteTransactionUseCase:
    return new_delete_transaction_usecase(transaction_repo)


def get_category_repository(session: Session = Depends(get_db)) -> CategoryRepository:
    return new_category_repository(session)


def get_get_category_list_usecase(
    category_repo: CategoryRepository = Depends(get_category_repository),
) -> GetCategoryListUseCase:
    return new_get_category_list_usecase(category_repo)
