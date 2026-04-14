from dataclasses import dataclass
from pathlib import Path
from typing import Any
import requests


@dataclass
class IntegralaiaProvider:
    base_url: str
    api_key: str
    timeout: int = 60
    extraction_timeout: int = 180

    @property
    def _headers(self) -> dict[str, str]:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def create_operation(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/mw/operations",
            headers=self._headers,
            json=payload,
            params=self._hash_params(doc_impoid),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def extract_sync_from_file(
        self,
        operation_id: str,
        file_path: str,
        document_type_code: str,
    ) -> dict[str, Any]:
        pdf = Path(file_path)
        if not pdf.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        headers = {"accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        with open(pdf, "rb") as file:
            response = requests.post(
                f"{self.base_url}/api/mw/operations/{operation_id}/documents/extract-sync",
                headers=headers,
                files={"file": (pdf.name, file, "application/pdf")},
                data={"document_type_code": document_type_code},
                timeout=self.extraction_timeout,
            )
        response.raise_for_status()
        return response.json()

    def get_document_types(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/api/mw/document-types",
            headers=self._headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def configure_extraction_schema(self, document_code: str, schema: dict[str, Any]) -> dict[str, Any]:
        response = requests.put(
            f"{self.base_url}/api/mw/document-types/{document_code}/extraction-schema",
            headers=self._headers,
            json=schema,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
