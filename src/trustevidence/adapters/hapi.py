from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(slots=True)
class HapiFhirAuditEventClient:
    """Minimal HAPI FHIR REST client used by the v2.0.0 conformance harness.

    The class posts AuditEvent resources to a running FHIR endpoint. It is not a
    FHIR-conformance assertion; v2.0.0 remain responsible for exact profiles and
    IG validation.
    """

    base_url: str = "http://localhost:8080/fhir"
    timeout_s: float = 10.0

    def _url(self, path: str) -> str:
        return self.base_url.rstrip("/") + "/" + path.lstrip("/")

    def capability_statement(self) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout_s) as client:
            response = client.get(self._url("metadata"), headers={"Accept": "application/fhir+json"})
            response.raise_for_status()
            return response.json()

    def post_audit_event(self, resource: dict[str, Any]) -> dict[str, Any]:
        if resource.get("resourceType") != "AuditEvent":
            raise ValueError("v2.0.0 HAPI client accepts AuditEvent resources only")
        with httpx.Client(timeout=self.timeout_s) as client:
            response = client.post(
                self._url("AuditEvent"),
                json=resource,
                headers={"Content-Type": "application/fhir+json", "Accept": "application/fhir+json"},
            )
            response.raise_for_status()
            return response.json()
