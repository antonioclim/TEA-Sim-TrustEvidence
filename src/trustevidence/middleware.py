from dataclasses import dataclass
from .schema import EnvelopeValidator
@dataclass
class TrustEvidenceMiddleware:
    backend: object; schema_validator: EnvelopeValidator = EnvelopeValidator()
    def emit(self,envelope): self.schema_validator.validate(envelope); return self.backend.append(envelope)
