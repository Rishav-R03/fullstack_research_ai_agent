import os
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base, Session # Import Session for type hinting

from dotenv import load_dotenv
load_dotenv()
Base = declarative_base()
from models.user_model import User

db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("POSTGRESQL_PASSWORD") 
db_name = os.getenv("DB_NAME", "smartresearchagent")
db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", 5432))

if not db_password:
    raise ValueError("POSTGRESQL_PASSWORD environment variable not set.")

db_url = URL.create(
    drivername="postgresql",
    username=db_user,
    password=db_password,
    database=db_name,
    host=db_host,
    port=db_port
)
engine = create_engine(db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
async def get_db():
    """
    Provides a SQLAlchemy database session for FastAPI routes.
    The session is automatically created for each request and closed afterwards.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def create_db_tables():
    """
    Creates all tables defined by Base's metadata in the connected database.
    This function discovers all models that inherit from Base (which must be imported).
    It should be called once, typically during application startup or via a dedicated script.
    In production, consider using Alembic for schema migrations.
    """
    print("Attempting to create database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created (or already exist).")
if __name__ == "__main__":
    create_db_tables()
    print("Database setup process initiated. Check your PostgreSQL logs for table creation.")