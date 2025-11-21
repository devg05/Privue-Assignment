import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


def validate_database_url() -> None:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or not DATABASE_URL.strip():
        raise RuntimeError(
            "DATABASE_URL is missing or empty. "
            "Set DATABASE_URL in your .env file, example:\n"
            "DATABASE_URL=postgresql://user:pass@localhost:5432/dbname"
        )
    return DATABASE_URL


def validate_database_echo() -> None:
    raw_echo = os.getenv("DATABASE_ECHO", "false").strip().lower()

    if raw_echo in ("1", "true", "yes", "y", "on"):
        DATABASE_ECHO = True
    elif raw_echo in ("0", "false", "no", "n", "off"):
        DATABASE_ECHO = False
    else:
        raise RuntimeError(
            f"Invalid DATABASE_ECHO value: '{raw_echo}'. "
            "Use true/false, 1/0, yes/no."
        )
    return DATABASE_ECHO