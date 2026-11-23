
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv(
        "APP_NAME",
        "Enterprise Knowledge & Workflow Copilot",
    )

    # SQL Server configuration
    DB_SERVER: str = os.getenv(
        "DB_SERVER",
        r"DESKTOP-S34C1RS\SQLEXPRESS",
    )

    DB_NAME: str = os.getenv(
        "DB_NAME",
        "EnterpriseCopilotDemo",
    )

    DB_DRIVER: str = os.getenv(
        "DB_DRIVER",
        "ODBC Driver 18 for SQL Server",
    )

    DB_TRUSTED_CONNECTION: bool = (
        os.getenv("DB_TRUSTED_CONNECTION", "true").lower()
        == "true"
    )

    # OpenAI configuration
    OPENAI_API_KEY: str = os.getenv(
        "OPENAI_API_KEY",
        "",
    )

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    GROQ_MODEL: str = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b"
    )


settings = Settings()
