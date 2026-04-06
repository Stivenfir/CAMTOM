from dataclasses import dataclass
import hashlib
from typing import Any
import requests


@dataclass
class IntegralaiaProvider:
    base_url: str
    api_key: str
    timeout: int = 60
    use_doc_hash: bool = False

    @property
    def _headers(self) -> dict[str, str]:
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _hash_params(self, doc_impoid: int | None) -> dict[str, str]:
        if not self.use_doc_hash or doc_impoid is None:
            return {}
        doc_text = str(doc_impoid)
        return {
            "doc_impoid": doc_text,
            "hash": hashlib.sha256(doc_text.encode("utf-8")).hexdigest(),
        }

    def create_operation_from_middleware(self, payload: dict[str, Any]) -> dict[str, Any]:
        doc_impoid = payload.get("doc_impoid")
        request_payload = {"doc_impoid": str(doc_impoid)}
        response = requests.post(
            f"{self.base_url}/api/mw/create-operation-from-mdw",
            headers=self._headers,
            json=request_payload,
            params=self._hash_params(doc_impoid),
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
            params=self._hash_params(doc_impoid),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
