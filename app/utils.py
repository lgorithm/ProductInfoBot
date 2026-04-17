
from app.database import DB_ENV
import psycopg
from langchain_postgres import PostgresChatMessageHistory


def get_chat_history(session_id: str):
    conn_info = DB_ENV.replace("postgresql+psycopg://", "postgresql://")
    conn = psycopg.connect(conn_info)

    return PostgresChatMessageHistory(
        "chat_history",
        session_id,
        sync_connection=conn
    )