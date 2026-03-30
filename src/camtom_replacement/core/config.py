from pydantic import BaseModel
from pydantic import Field
from pydantic import ConfigDict
import os


class Settings(BaseModel):
    """Configuración central del servicio."""

    model_config = ConfigDict(frozen=True)

    sql_server: str = Field(default_factory=lambda: os.getenv("SQL_SERVER", "172.16.10.54\\DBABC21"))
    sql_database: str = Field(default_factory=lambda: os.getenv("SQL_DATABASE", "Repecev2005_H"))
    sql_username: str = Field(default_factory=lambda: os.getenv("SQL_USERNAME", "Repecev2005"))
    sql_password: str = Field(default_factory=lambda: os.getenv("SQL_PASSWORD", ""))

    provider_base_url: str = Field(default_factory=lambda: os.getenv("PROVIDER_BASE_URL", "https://dev-visado-api-abcrepecev.integralaia.com"))
    provider_api_key: str = Field(default_factory=lambda: os.getenv("PROVIDER_API_KEY", ""))
    provider_timeout_seconds: int = Field(default_factory=lambda: int(os.getenv("PROVIDER_TIMEOUT_SECONDS", "60")))


def get_settings() -> Settings:
    return Settings()
