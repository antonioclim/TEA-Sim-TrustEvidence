#!/usr/bin/env python3
"""Compatibility wrapper for reviewer-facing result-schema validation."""
from pathlib import Path
import runpy, sys
if __name__ == '__main__':
    script = Path(__file__).resolve().parents[1] / 'experiments' / 'validate_results.py'
    sys.argv[0] = str(script)
    runpy.run_path(str(script), run_name='__main__')
