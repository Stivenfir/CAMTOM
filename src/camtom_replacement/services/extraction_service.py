from typing import Any
from pathlib import Path
from datetime import date

from camtom_replacement.providers.integralaia_provider import IntegralaiaProvider
from camtom_replacement.repositories.tracking_repository import TrackingRepository


class ExtractionService:
    """Orquesta extracción con nuevo proveedor y tracking existente."""

    def __init__(
        self,
        tracking_repository: TrackingRepository,
        provider: IntegralaiaProvider,
        document_type_code: str = "FACTURACOMERCIAL",
    ) -> None:
        self.tracking_repository = tracking_repository
        self.provider = provider
        self.document_type_code = document_type_code

    def process_doc_impoid(self, doc_impoid: int) -> list[dict[str, Any]]:
        pending_docs = self.tracking_repository.get_pending_documents(doc_impoid)
        results: list[dict[str, Any]] = []

        for ruta_factura, procesar_factura_id, _ in pending_docs:
            self.tracking_repository.mark_start(procesar_factura_id)
            try:
                operation = self.provider.create_operation(
                    self._build_operation_payload(doc_impoid, ruta_factura)
                )
                extraction = self.provider.extract_sync_from_file(
                    operation_id=operation["id"],
                    file_path=ruta_factura,
                    document_type_code=self.document_type_code,
                )
                self.tracking_repository.mark_success(procesar_factura_id)
                results.append(
                    {
                        "procesar_factura_id": procesar_factura_id,
                        "ruta_factura": ruta_factura,
                        "operation": operation,
                        "extraction": extraction,
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

    def process_folder_documents(self, doc_impoid: int, folder_path: str) -> dict[str, Any]:
        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)

        files = sorted(path for path in folder.iterdir() if path.is_file())
        results: list[dict[str, Any]] = []

        operation_payload = {
            "doc_impoid": str(doc_impoid),
            "do_number": str(doc_impoid),
            "operation_date": date.today().isoformat(),
            "client_name": "",
            "executive_name": "",
            "details": {},
        }
        for file_path in files:
            try:
                operation = self.provider.create_operation(operation_payload)
                extraction = self.provider.extract_sync_from_file(
                    operation_id=operation["id"],
                    file_path=str(file_path.resolve()),
                    document_type_code=self.document_type_code,
                )
                results.append(
                    {
                        "file_name": file_path.name,
                        "operation": operation,
                        "extraction": extraction,
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "file_name": file_path.name,
                        "error": str(exc),
                    }
                )

        return {
            "doc_impoid": doc_impoid,
            "folder_path": str(folder.resolve()),
            "files_found": len(files),
            "results": results,
        }

    def _build_operation_payload(self, doc_impoid: int, ruta_factura: str) -> dict[str, Any]:
        return {
            "doc_impoid": str(doc_impoid),
            "do_number": str(doc_impoid),
            "operation_date": date.today().isoformat(),
            "client_name": "",
            "executive_name": "",
            "details": {"ruta_factura": ruta_factura},
        }
