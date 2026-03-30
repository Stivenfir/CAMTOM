from fastapi import FastAPI

from camtom_replacement.core.config import get_settings
from camtom_replacement.db.sql_server import SqlServerClient
from camtom_replacement.providers.integralaia_provider import IntegralaiaProvider
from camtom_replacement.repositories.tracking_repository import TrackingRepository
from camtom_replacement.services.extraction_service import ExtractionService


def create_app() -> FastAPI:
    settings = get_settings()

    db_client = SqlServerClient(
        server=settings.sql_server,
        database=settings.sql_database,
        username=settings.sql_username,
        password=settings.sql_password,
    )

    tracking_repository = TrackingRepository(db_client)
    provider = IntegralaiaProvider(
        base_url=settings.provider_base_url,
        api_key=settings.provider_api_key,
        timeout=settings.provider_timeout_seconds,
    )
    extraction_service = ExtractionService(tracking_repository, provider)

    app = FastAPI(title="CAMTOM Replacement - Integralaia")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/v2/procesarfactura/{doc_impoid}")
    def procesar_factura(doc_impoid: int):
        return {
            "doc_impoid": doc_impoid,
            "results": extraction_service.process_doc_impoid(doc_impoid),
        }

    return app


app = create_app()
