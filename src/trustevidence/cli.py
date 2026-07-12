"""Small command-line interface for schema and semantic validation."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .validators import validate_curation_result, validate_envelope, validate_monitoring_event


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="teasim")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate a JSON object")
    validate.add_argument("kind", choices=["event", "envelope", "result"])
    validate.add_argument("path", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    instance = json.loads(args.path.read_text(encoding="utf-8"))
    validator = {"event": validate_monitoring_event, "envelope": validate_envelope, "result": validate_curation_result}[args.kind]
    result = validator(instance)
    payload = {
        "accepted": result.accepted,
        "issues": [asdict(issue) for issue in result.issues],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
