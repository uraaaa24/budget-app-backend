from pydantic import BaseModel


class CreateTransactionResponseSchema(BaseModel):
    transaction_id: str
