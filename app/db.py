# app/db.py
from __future__ import annotations
import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "db")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB   = os.getenv("MYSQL_DB", "monitors")
MYSQL_USER = os.getenv("MYSQL_USER", "app")
MYSQL_PW   = os.getenv("MYSQL_PASSWORD", "secret")

DB_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PW}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
engine = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def wait_for_db(max_tries: int = 60, delay: float = 2.0) -> None:
    """Block until a simple SELECT 1 succeeds against MySQL."""
    for _ in range(max_tries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception:
            time.sleep(delay)
    raise RuntimeError("Database not reachable")