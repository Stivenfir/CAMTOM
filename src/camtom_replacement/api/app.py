from fastapi import FastAPI
from pydantic import BaseModel

from camtom_replacement.core.config import get_settings
from camtom_replacement.db.sql_server import SqlServerClient
from camtom_replacement.providers.integralaia_provider import IntegralaiaProvider
from camtom_replacement.repositories.tracking_repository import TrackingRepository
from camtom_replacement.services.extraction_service import ExtractionService


class ProcessFolderRequest(BaseModel):
    doc_impoid: int
    folder_path: str = "./facturas_inbox"


def create_app() -> FastAPI:
    settings = get_settings(validate=False)

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
    extraction_service = ExtractionService(
        tracking_repository,
        provider,
        document_type_code=settings.default_document_type_code,
    )

    app = FastAPI(title="CAMTOM Replacement - Integralaia")

    @app.on_event("startup")
    def validate_env() -> None:
        settings.validate_required()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/config-check")
    def config_check() -> dict[str, str | int | bool]:
        return {
            "sql_server": settings.sql_server,
            "sql_database": settings.sql_database,
            "provider_base_url": settings.provider_base_url,
            "provider_has_api_key": bool(settings.provider_api_key and settings.provider_api_key != "REEMPLAZAR_CON_TOKEN_REAL"),
            "provider_timeout_seconds": settings.provider_timeout_seconds,
            "default_document_type_code": settings.default_document_type_code,
            "app_host": settings.app_host,
            "app_port": settings.app_port,
            "app_reload": settings.app_reload,
        }

    @app.post("/api/v2/procesarfactura/{doc_impoid}")
    def procesar_factura(doc_impoid: int):
        return {
            "doc_impoid": doc_impoid,
            "results": extraction_service.process_doc_impoid(doc_impoid),
        }

    @app.post("/api/v2/procesar-carpeta")
    def procesar_carpeta(request: ProcessFolderRequest):
        return extraction_service.process_folder_documents(
            doc_impoid=request.doc_impoid,
            folder_path=request.folder_path,
        )

    return app


app = create_app()
