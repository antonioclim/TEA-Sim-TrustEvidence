# Environment disclosure

The release candidate supports Python 3.13.x and declares `>=3.13,<3.14`. The locked local audit environment uses Python 3.13.5 on Linux; hosted Route C gates use the Python 3.13 release available on GitHub-hosted Ubuntu 24.04 and record the exact interpreter in the workflow transcript.

`tool_versions.json` records the package and principal local/hosted tool boundaries. `requirements-lock-py313-linux.txt` records the pinned Python dependency set used by hosted release checks and fresh-extraction validation.

The official FHIR regression additionally uses Node 22, Java 17, Ruby 3.3, SUSHI 3.20.0 and Jekyll 4.4.1. These tools validate the declared synthetic corpus; they do not establish universal FHIR/BALP conformance or certification.

The workflow uses commit-pinned external GitHub Actions and read-only repository permissions. One-time evidence-materialisation jobs are removed after C5; the C6 candidate job builds, audits and executes the curated archive after fresh extraction.
