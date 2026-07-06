# Quick start

Run the local checks from the archive root. The commands below are intended for a local Python environment with the packages listed in `requirements-core.txt` and `requirements-test.txt`.

```bash
python -m compileall src tests experiments scripts
python -m pytest tests -q
python figures/scripts/generate_jcis_figures.py
make quick
make evaluation-smoke
```

The commands generate local validation outputs under `validation/` and `results/`. These runtime folders are intentionally excluded from the distributed checksums and may be deleted after inspection.
