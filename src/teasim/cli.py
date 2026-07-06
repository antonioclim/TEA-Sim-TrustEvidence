from __future__ import annotations
import argparse
from pathlib import Path
from .compat.v1_5_1 import run_v1_5_1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="teasim", description="TEA-Sim v2 utilities")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("reproduce-v1", help="Run the v1.5.1 compatibility shim")
    p.add_argument("--output-dir", default="outputs/v1_5_1_reproduction", help="directory for regenerated v1 outputs")
    args = parser.parse_args(argv)
    if args.cmd == "reproduce-v1":
        return run_v1_5_1(Path(args.output_dir))
    return 2
