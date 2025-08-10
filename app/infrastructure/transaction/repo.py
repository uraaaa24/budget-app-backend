from sqlalchemy import select

from app.domain.transaction.repo import TransactionRepository
from app.domain.transaction.transaction import Transaction
from app.infrastructure.transaction.dto import TransactionDTO


class TransactionRepositoryImpl(TransactionRepository):
    """SQLAlchemy implementation of TransactionRepository."""
    
    def __init__(self, session):
        """Initialize with a SQLAlchemy session."""
        self.session = session

    def find_all(self) -> list[Transaction]:
        """Retrieve all transactions."""
        rows = self.session.execute(select(TransactionDTO)).scalars().all()
        return [row.to_entity() for row in rows]

    def add(self, entity: Transaction) -> None:
        """Add a new transaction."""
        if self.session.get(TransactionDTO, entity.id) is not None:
            raise KeyError(f"Transaction already exists: {entity.id}")

        self.session.add(TransactionDTO.from_entity(entity))

    def update(self, entity: Transaction) -> None:
        """Update an existing transaction."""
        row = self.session.get(TransactionDTO, entity.id)
        if row is None:
            raise KeyError(f"Transaction not found: {entity.id}")
        
        row.account_id = entity.account_id
        row.type = entity.type.value
        row.amount = entity.amount.value
        row.occurred_at = entity.occurred_at
        row.category_id = entity.category_id
        row.description = entity.description
        row.created_at = entity.created_at
        row.updated_at = entity.updated_at
