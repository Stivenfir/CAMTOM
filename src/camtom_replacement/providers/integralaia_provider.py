from dataclasses import dataclass
from typing import Any
import requests


@dataclass
class IntegralaiaProvider:
    base_url: str
    api_key: str
    timeout: int = 60

    @property
    def _headers(self) -> dict[str, str]:
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def create_operation_from_middleware(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/middleware/create-operation-from-mdw",
            headers=self._headers,
            json=payload,
            timeout=self.timeout,
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

    def get_extracted_data(self, doc_impoid: int) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/api/mw/operations/{doc_impoid}/documents/extracted-data",
            headers=self._headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
