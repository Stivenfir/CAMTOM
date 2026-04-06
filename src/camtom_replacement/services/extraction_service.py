from typing import Any
from pathlib import Path
from datetime import date

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

        for _, procesar_factura_id, _ in pending_docs:
            self.tracking_repository.mark_start(procesar_factura_id)

        try:
            operation_payload = self.tracking_repository.build_operation_payload(
                doc_impoid=doc_impoid,
                documents=pending_docs,
            )
            operation = self.provider.create_operation(operation_payload)
            extracted_data = self.provider.get_extracted_data(doc_impoid)
            has_global_error = False
        except Exception as exc:
            operation = None
            extracted_data = None
            has_global_error = True
            global_error = str(exc)

        for ruta_factura, procesar_factura_id, _ in pending_docs:
            if not has_global_error:
                self.tracking_repository.mark_success(procesar_factura_id)
                results.append(
                    {
                        "procesar_factura_id": procesar_factura_id,
                        "ruta_factura": ruta_factura,
                        "operation": operation,
                        "extracted_data": extracted_data,
                    }
                )
                continue

            self.tracking_repository.mark_error(procesar_factura_id, global_error)
            results.append(
                {
                    "procesar_factura_id": procesar_factura_id,
                    "ruta_factura": ruta_factura,
                    "error": global_error,
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
            "details": {
                "documents": [
                    {
                        "file_name": file_path.name,
                        "ruta_factura": str(file_path.resolve()),
                    }
                    for file_path in files
                ]
            },
        }

        try:
            operation = self.provider.create_operation(operation_payload)
            extracted_data = self.provider.get_extracted_data(doc_impoid)
            for file_path in files:
                results.append(
                    {
                        "file_name": file_path.name,
                        "operation": operation,
                        "extracted_data": extracted_data,
                    }
                )
        except Exception as exc:
            for file_path in files:
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
