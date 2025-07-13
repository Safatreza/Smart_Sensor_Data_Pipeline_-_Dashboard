import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Get DATABASE_URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../data/processed.db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_engine() -> Engine:
    """Return the SQLAlchemy engine."""
    return engine

def get_session():
    """Return a new SQLAlchemy session."""
    return SessionLocal()

def is_postgres():
    """Return True if the backend is PostgreSQL/TimescaleDB."""
    return DATABASE_URL.startswith("postgresql")

# Optionally, add TimescaleDB hypertable creation logic
from sqlalchemy import text

def create_timescale_hypertable(table_name: str, time_column: str = "timestamp"):
    """Convert a table to a TimescaleDB hypertable if using PostgreSQL/TimescaleDB."""
    if is_postgres():
        with engine.connect() as conn:
            try:
                conn.execute(text(f"SELECT create_hypertable('{table_name}', '{time_column}', if_not_exists => TRUE);"))
            except SQLAlchemyError as e:
                print(f"Hypertable creation failed or already exists: {e}") 