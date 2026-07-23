#!/usr/bin/env python3
"""Execute the Route C HIE hero-case builder with TE-JCS-admissible fixtures.

FHIR decimals are valid JSON numbers, but the current TE-JCS-1 application
profile deliberately excludes Python floating-point values. The Route C source
fixture therefore uses clinically plausible integer-valued laboratory results
for its deterministic commitment bytes. This wrapper makes that bounded choice
explicit without changing the v2.1 personal-monitoring canonicalisation rules.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments import build_hie_hero_case as implementation  # noqa: E402

DEFAULT_OUTPUT = implementation.DEFAULT_OUTPUT
FHIR_RESOURCES = implementation.FHIR_RESOURCES
HIE_COMMITMENT_CONTEXT = implementation.HIE_COMMITMENT_CONTEXT
HIE_REPRESENTATION_PROFILE = implementation.HIE_REPRESENTATION_PROFILE
NONCE = implementation.NONCE

_original_source_resources = implementation.source_resources


def source_resources():
    resources = _original_source_resources()
    resources["observation-potassium-hie-001"]["valueQuantity"]["value"] = 4
    resources["observation-creatinine-hie-001"]["valueQuantity"]["value"] = 1
    return resources


implementation.source_resources = source_resources
build_outputs = implementation.build_outputs
write_outputs = implementation.write_outputs
check_outputs = implementation.check_outputs


def main() -> None:
    implementation.main()


if __name__ == "__main__":
    main()
