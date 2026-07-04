#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

def save(name: str):
    for ext in ("svg", "pdf", "png"):
        plt.savefig(OUT / f"{name}.{ext}", bbox_inches="tight")
    plt.close()

fig, ax = plt.subplots(figsize=(8,4))
ax.axis("off")
items = [("Python harness",0.5,0.80),("HAPI FHIR / PostgreSQL / Trillian / Rekor / Fabric containers",0.5,0.55),(" measurement protocol and returned results bundle",0.5,0.30)]
for text, x, y in items:
    ax.text(x, y, text, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.45", fill=False))
ax.annotate("", xy=(0.5,0.64), xytext=(0.5,0.72), arrowprops=dict(arrowstyle="->"))
ax.annotate("", xy=(0.5,0.39), xytext=(0.5,0.47), arrowprops=dict(arrowstyle="->"))
ax.set_title("Implementation and measurement stack")
save("figure_05_stack")
