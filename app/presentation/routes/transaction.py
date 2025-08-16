from fastapi import APIRouter

router = APIRouter(tags=["transaction"])


@router.get("/transactions")
async def get_transactions():
    """Endpoint to retrieve transactions"""
    return {"message": "This endpoint will return transactions."}
