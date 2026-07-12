# Environment disclosure

The audited release-candidate execution uses Python 3.13.5 on Linux. The package therefore declares Python 3.13.x as its supported interpreter range for v2.1.0.

`tool_versions.json` records the locally executed environment. `requirements-lock-py313-linux.txt` records the pinned reference dependency set. Python 3.12 could not be installed in the audit environment and is not claimed as supported by this release.

The public hosted-CI workflow is omitted because no hosted run was observed before archive finalisation. Reviewers should use the documented local `make release-check` pathway.
