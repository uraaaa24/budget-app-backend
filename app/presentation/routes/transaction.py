from fastapi import APIRouter, Depends

from app.core.auth import get_current_user

router = APIRouter(tags=["transaction"])


@router.get("/transactions")
async def get_transactions(user_id: str = Depends(get_current_user)):
    """Retrieve transactions for the current user"""
    # Placeholder for actual transaction retrieval logic
    return {"message": f"Transactions for user {user_id}"}
