# Manuscript figure generation

The JCIS manuscript figures are generated from public-safe repository evidence
extracts and layout specifications rather than adjusted manually in a word
processor. The canonical command is:

```bash
python figures/scripts/generate_jcis_figures.py
```

The script reads `figure_sources/*.csv` and writes SVG, PDF and 300 dpi PNG
outputs to `figures/outputs/`. The source CSVs include standards-facing,
backend, workload and property-validation extracts together with explicit layout
specifications for boxes and routed connectors.

The figures are bounded evidence visualisations. They do not add independent
FHIR/BALP conformance, A1/A3 execution, full external-dataset extraction,
TLA+/Alloy execution or expert-validation claims.
