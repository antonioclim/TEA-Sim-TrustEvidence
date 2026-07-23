#!/usr/bin/env python3
"""Require immutable full-SHA references for external GitHub Actions."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
USE = re.compile(r"(?m)^\s*-?\s*uses:\s*([^@\s]+)@([^\s#]+)")
FULL_SHA = re.compile(r"^[0-9a-fA-F]{40}$")


def main() -> int:
    errors: list[str] = []
    pins: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        for target, revision in USE.findall(text):
            if target.startswith("./"):
                continue
            pins.append(f"{target}@{revision}")
            if not FULL_SHA.fullmatch(revision):
                errors.append(
                    f"mutable action reference in {path.relative_to(ROOT)}: "
                    f"{target}@{revision}"
                )
    if not pins:
        errors.append("no external action references found")
    if errors:
        print("ACTION-PINS: FAIL")
        print("\n".join(errors))
        return 1
    print(f"ACTION-PINS: PASS ({len(pins)} immutable references)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
