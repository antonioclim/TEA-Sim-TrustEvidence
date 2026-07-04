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

fig, ax = plt.subplots(figsize=(9, 4))
ax.axis("off")
labels = ["FHIR/BALP event", "TrustEvidence\nemission boundary", "Evidence backend\nA1/A2/A3", "Verifier/auditor"]
xs = [0.08, 0.34, 0.62, 0.86]
for x, lab in zip(xs, labels):
    ax.text(x, 0.55, lab, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.5", fill=False))
for a, b in zip(xs[:-1], xs[1:]):
    ax.annotate("", xy=(b-0.11, 0.55), xytext=(a+0.11, 0.55), arrowprops=dict(arrowstyle="->"))
ax.text(0.5, 0.15, "Clinical payload custody remains outside the evidence backend", ha="center")
ax.set_title("Evidence boundary and verification path")
save("figure_01_boundary")
