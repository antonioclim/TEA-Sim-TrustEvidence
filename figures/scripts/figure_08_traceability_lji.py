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

fig, ax = plt.subplots(figsize=(9,3.5))
ax.axis("off")
labels = ["Legal / standards\nobligation", "Technical\nrequirement", "TrustEvidence\nmechanism", "Verification\ntest", "LJI 2.0\ngate"]
xs = [0.08, 0.29, 0.50, 0.71, 0.91]
for x, l in zip(xs, labels):
    ax.text(x, 0.55, l, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.35", fill=False))
for a, b in zip(xs[:-1], xs[1:]):
    ax.annotate("", xy=(b-0.075,0.55), xytext=(a+0.075,0.55), arrowprops=dict(arrowstyle="->"))
ax.text(0.5,0.15,"Interpretive traceability only; no legal-compliance conclusion",ha="center")
ax.set_title("Legal traceability and proportionality gate")
save("figure_08_traceability_lji")
