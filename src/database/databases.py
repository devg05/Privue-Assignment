from typing import Iterator
from src.utils.validate_db_url import validate_database_url, validate_database_echo

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


DATABASE_URL = validate_database_url()
DATABASE_ECHO = validate_database_echo()


engine = create_engine(url=DATABASE_URL, echo=DATABASE_ECHO, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
