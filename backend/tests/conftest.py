import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from scrai_core.core.persistence import Base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use a separate test database
DATABASE_URL = os.getenv("DATABASE_URL")

@pytest.fixture(scope="session")
def engine():
    """Creates a new database engine for the test session."""
    return create_engine(DATABASE_URL)

@pytest.fixture(scope="session")
def tables(engine):
    """Creates all tables before the test session and drops them after."""
    # Import all models here to ensure they are registered with Base
    from scrai_core.agents.models import Agent, EpisodicMemory
    from scrai_core.world.models import WorldObject
    
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    """
    Provides a transactional scope for tests. Each test will run within a
    transaction, which is rolled back at the end of the test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
