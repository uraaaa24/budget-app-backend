from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

_NAMING = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=_NAMING)


class Database:
    def __init__(self, url: str, **pool):
        self.engine: Engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=pool.get("recycle", 1800),
            pool_size=pool.get("size", 5),
            max_overflow=pool.get("max_overflow", 10),
            pool_timeout=pool.get("timeout", 30),
            echo=getattr(settings, "DB_ECHO", False),
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    @contextmanager
    def session(self) -> Iterator[Session]:
        with self.SessionLocal() as db:
            try:
                yield db
                db.commit()
            except Exception:
                db.rollback()
                raise

    def ping(self) -> bool:
        try:
            with self.engine.connect() as conn:
                return conn.execute(text("SELECT 1")).scalar_one() == 1
        except Exception:
            return False

    def dispose(self) -> None:
        self.engine.dispose()


db = Database(settings.DATABASE_URL)


def get_db() -> Iterator[Session]:
    with db.session() as s:
        yield s
