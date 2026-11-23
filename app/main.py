
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import check_database_connection

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description=(
        "An enterprise assistant with secure knowledge "
        "retrieval, MCP tools, and agentic workflows."
    ),
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "application": settings.APP_NAME,
    }


@app.get("/health/db", tags=["Health"])
def database_health_check():
    try:
        details = check_database_connection()
        return {
            "status": "connected",
            "database": details["database_name"],
            "server": details["server_name"],
        }
    except SQLAlchemyError:
        # Avoid returning database connection details to clients.
        raise HTTPException(
            status_code=503,
            detail="Database connection failed.",
        ) from None
