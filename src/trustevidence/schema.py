import json
from importlib.resources import files
from jsonschema import Draft202012Validator
from .errors import SCHEMA_VALIDATION, TrustEvidenceError
def load_schema(): return json.loads(files("trustevidence.schemas").joinpath("trust_evidence_envelope.schema.json").read_text())
class EnvelopeValidator:
    def __init__(self,schema=None): self.schema=schema or load_schema(); Draft202012Validator.check_schema(self.schema); self.validator=Draft202012Validator(self.schema)
    def validate(self,envelope):
        errs=sorted(self.validator.iter_errors(envelope),key=lambda e:list(e.path))
        if errs: raise TrustEvidenceError(SCHEMA_VALIDATION,"; ".join(e.message for e in errs[:3]))
