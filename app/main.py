from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.register_app import register_app

app = register_app()


# TODO: An example endpoint to demonstrate database usage
@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    """List all items in the budget."""
    # db.query(...), db.execute(...), etc.
    return []
