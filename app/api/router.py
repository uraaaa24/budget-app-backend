from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/")
def root() -> dict[str, str]:
    return {"message": "Budget App API v1"}