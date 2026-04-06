import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


# Carga .env desde la raíz del proyecto si existe
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseModel):
    """Configuración central del servicio."""

    model_config = ConfigDict(frozen=True)

    sql_server: str = Field(default_factory=lambda: os.getenv("SQL_SERVER", "172.16.10.54\\DBABC21"))
    sql_database: str = Field(default_factory=lambda: os.getenv("SQL_DATABASE", "Repecev2005_H"))
    sql_username: str = Field(default_factory=lambda: os.getenv("SQL_USERNAME", "Repecev2005"))
    sql_password: str = Field(default_factory=lambda: os.getenv("SQL_PASSWORD", ""))

    provider_base_url: str = Field(default_factory=lambda: os.getenv("PROVIDER_BASE_URL", "https://dev-visado-api-abcrepecev.integralaia.com"))
    provider_api_key: str = Field(default_factory=lambda: os.getenv("PROVIDER_API_KEY", ""))
    provider_use_doc_hash: bool = Field(default_factory=lambda: os.getenv("PROVIDER_USE_DOC_HASH", "false").lower() == "true")
    provider_timeout_seconds: int = Field(default_factory=lambda: int(os.getenv("PROVIDER_TIMEOUT_SECONDS", "60")))

    app_host: str = Field(default_factory=lambda: os.getenv("APP_HOST", "0.0.0.0"))
    app_port: int = Field(default_factory=lambda: int(os.getenv("APP_PORT", "8000")))
    app_reload: bool = Field(default_factory=lambda: os.getenv("APP_RELOAD", "false").lower() == "true")

    def validate_required(self) -> None:
        return None


def get_settings(validate: bool = True) -> Settings:
    settings = Settings()
    if validate:
        settings.validate_required()
    return settings
