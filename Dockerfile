FROM python:3.11-slim

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation and system site packages installation 
ENV UV_COMPILE_BYTECODE=1
ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Copy application requirements
COPY pyproject.toml .

# Install dependencies into system Python using uv
RUN uv pip install --system fastapi uvicorn langchain langchain-openai langchain-community langchain-postgres psycopg[binary,pool] sqlalchemy pydantic

# Copy the rest of the application
COPY . /app

# Expose port
EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
