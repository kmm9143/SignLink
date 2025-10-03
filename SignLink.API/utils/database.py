from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os

# Load from environment variable for security
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()