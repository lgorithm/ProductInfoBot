from langchain_core.tools import tool
from sqlalchemy import inspect
from app.database import engine
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings
import os
from sqlalchemy import text
from app.schemas import NLP_to_Sql
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings

os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3).with_structured_output(NLP_to_Sql)
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)
pc = Pinecone(
    api_key=settings.PINECONE_API_KEY,
)
index = pc.Index("personal-care-products")
@tool
def get_database_schema() -> str:
    """
    Returns database schema including tables and columns.
    """
    inspector = inspect(engine)
    schema_info = ""

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        col_names = [col["name"] for col in columns]
        schema_info += f"Table: {table_name}\nColumns: {', '.join(col_names)}\n\n"

    return schema_info

@tool
def nl_to_sql_and_query(user_query: str, db_schema: str) -> str:
    """
    Converts natural language to SQL using schema and executes it.
    """

    prompt = f"""
    You are a SQL expert.

    Given the database schema:
    {db_schema}

    Convert the following natural language query into SQL.
    
    Rules:
    - Only generate SELECT queries
    - Do NOT modify database
    - Use correct table/column names from schema
    - Return ONLY SQL query (no explanation)

    User Query:
    {user_query}
    """

    try:
        sql_query = model.invoke(prompt).sql_query
        print("Generated SQL Query:", sql_query)
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
        print("SQL Query Result:", rows)
        return str(rows)

    except Exception as e:
        return f"Error: {str(e)}"
    
@tool
def semantic_product_search(query: str) -> str:
    """
    Use this tool for semantic search when SQL search fails
    or when user query is vague, descriptive, or natural language.
    """

    try:
        print("Performing semantic search for query:", query)
        results = pinecone_search(query)

        if not results:
            return "No semantic matches found."

        return str(results)

    except Exception as e:
        return f"Semantic search error: {str(e)}"
@tool
def escalate_to_human(topic: str) -> str:
    """
    Use this tool when the user asks about offers, refunds, or returns.
    Returns customer care contact details.
    """
    return "Please contact our human representative at 9748867349 regarding your inquiry about offers, returns, or refunds."

def pinecone_search(query: str):
    query_vector = embeddings.embed_query(query)

    results = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True
    )

    matches = []
    for match in results["matches"]:
        if match["score"] > 0.7:  # threshold
            matches.append({
                "name": match["metadata"].get("name"),
                "description": match["metadata"].get("description"),
                "category": match["metadata"].get("category"),
                "price": match["metadata"].get("price"),
                "benefits": match["metadata"].get("benefits"),
                "score": match["score"]
            })

    return matches
tools = [escalate_to_human, nl_to_sql_and_query, get_database_schema, semantic_product_search]
