from typing import Any

from camtom_replacement.providers.integralaia_provider import IntegralaiaProvider
from camtom_replacement.repositories.tracking_repository import TrackingRepository


class ExtractionService:
    """Orquesta extracción con nuevo proveedor y tracking existente."""

    def __init__(self, tracking_repository: TrackingRepository, provider: IntegralaiaProvider) -> None:
        self.tracking_repository = tracking_repository
        self.provider = provider

    def process_doc_impoid(self, doc_impoid: int) -> list[dict[str, Any]]:
        pending_docs = self.tracking_repository.get_pending_documents(doc_impoid)
        results: list[dict[str, Any]] = []

        for ruta_factura, procesar_factura_id, soporte_id in pending_docs:
            self.tracking_repository.mark_start(procesar_factura_id)
            try:
                operation_payload = {
                    "doc_impoid": doc_impoid,
                    "procesar_factura_id": procesar_factura_id,
                    "soporte_id": soporte_id,
                    "ruta_factura": ruta_factura,
                }
                operation = self.provider.create_operation_from_middleware(operation_payload)
                extracted_data = self.provider.get_extracted_data(doc_impoid)

                self.tracking_repository.mark_success(procesar_factura_id)
                results.append(
                    {
                        "procesar_factura_id": procesar_factura_id,
                        "ruta_factura": ruta_factura,
                        "operation": operation,
                        "extracted_data": extracted_data,
                    }
                )
            except Exception as exc:
                self.tracking_repository.mark_error(procesar_factura_id, str(exc))
                results.append(
                    {
                        "procesar_factura_id": procesar_factura_id,
                        "ruta_factura": ruta_factura,
                        "error": str(exc),
                    }
                )

        return results
