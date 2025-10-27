from scrai_core.core.persistence import Base, engine
# Import all models here so that they are registered with SQLAlchemy's metadata
from scrai_core.agents.models import Agent, EpisodicMemory
from scrai_core.world.models import WorldObject

def init_db():
    """
    Creates all database tables based on the SQLAlchemy models.
    """
    print("Dropping existing database tables (if any)...")
    Base.metadata.drop_all(bind=engine)
    print("Existing tables dropped.")
    print("Creating all database tables based on models...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
