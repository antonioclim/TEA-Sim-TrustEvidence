# Quickstart

```bash
python -m compileall src 04_formalisation
PYTHONPATH=src python -m pytest -q 04_formalisation/hypothesis_tests/test_merkle_properties.py --hypothesis-show-statistics -p no:cacheprovider
PYTHONPATH=src python 04_formalisation/bounded_model/bounded_model_check.py
python scripts/repository_check.py
python scripts/verify_sha256sums.py SHA256SUMS.txt
```
