from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define the database file path
# It's good practice to keep the DB in a dedicated data folder
DB_DIR = "app/data"
DB_NAME = "locations.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DB_DIR}/{DB_NAME}"

# Ensure the data directory exists
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# create_engine for SQLite:
# 'check_same_thread': False is required for SQLite in FastAPI because
# multiple threads might interact with the DB during a single request.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# This creates a 'SessionLocal' class.
# Each instance of this class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models to inherit from
Base = declarative_base()