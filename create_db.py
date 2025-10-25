import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
if not database_exists(engine.url):
    create_database(engine.url)

print(f"Database at {engine.url} created or already exists.")
