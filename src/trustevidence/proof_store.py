from dataclasses import dataclass, field
from .errors import UNAVAILABLE_PROOF, TrustEvidenceError
@dataclass
class InMemoryProofStore:
    prefix: str="urn:te:proof"; _items: dict=field(default_factory=dict); _counter:int=0
    def put(self,kind,proof): self._counter+=1; ref=f"{self.prefix}:{kind}:{self._counter:06d}"; self._items[ref]=proof; return ref
    def get(self,ref):
        if ref not in self._items: raise TrustEvidenceError(UNAVAILABLE_PROOF,f"proof unavailable: {ref}")
        return self._items[ref]
