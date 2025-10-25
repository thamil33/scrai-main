from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection string from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# SQLAlchemy SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for declarative models
Base = declarative_base()

def get_engine():
    """Returns the SQLAlchemy engine."""
    return engine

def get_session():
    """Generator function to get a database session."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()

def init_db():
    """Initializes the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
