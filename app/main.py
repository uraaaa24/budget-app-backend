from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.api import health_router
from app.core.database import get_db
from app.core.logging import setup_logging
from app.middleware import RequestLoggingMiddleware

setup_logging()

app = FastAPI(
    title="Budget App API",
    description="Personal budget management application",
    version="1.0.0",
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(health_router)


# TODO: An example endpoint to demonstrate database usage
@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    """List all items in the budget."""
    # db.query(...), db.execute(...), etc.
    return []
