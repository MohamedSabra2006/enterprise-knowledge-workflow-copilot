
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from app.core.config import settings

from sqlalchemy.orm import sessionmaker

def build_connection_string() -> str:
    parts = [
        f"DRIVER={{{settings.DB_DRIVER}}}",
        f"SERVER={settings.DB_SERVER}",
        f"DATABASE={settings.DB_NAME}",
        (
            "Trusted_Connection=yes"
            if settings.DB_TRUSTED_CONNECTION
            else "Trusted_Connection=no"
        ),
        "Encrypt=yes",
        "TrustServerCertificate=yes",
    ]

    return ";".join(parts)


connection_url = URL.create(
    "mssql+pyodbc",
    query={
        "odbc_connect": build_connection_string(),
    },
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    pool_recycle=1800,
)


def check_database_connection() -> dict:
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT
                    DB_NAME() AS database_name,
                    @@SERVERNAME AS server_name,
                    1 AS connected
                """
            )
        ).mappings().one()

        return dict(result)



SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()