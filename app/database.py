import psycopg
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings
from langchain_postgres import PostgresChatMessageHistory
DB_ENV = settings.DATABASE_URL

if DB_ENV.startswith("postgresql://"):
    # SQLAlchemy 2 requires postgresql+psycopg structure
    DB_URL = DB_ENV.replace("postgresql://", "postgresql+psycopg://")
else:
    DB_URL = DB_ENV

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_chat_table():
    conn_info = DB_ENV.replace("postgresql+psycopg://", "postgresql://")
    conn = psycopg.connect(conn_info)

    PostgresChatMessageHistory.create_tables(conn, "chat_history")

    conn.close()