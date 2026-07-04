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
states = ["Observed", "Prepared", "Signed", "Submitted", "Accepted", "Failure\nartefact"]
xs = [0.05, 0.22, 0.39, 0.56, 0.73, 0.90]
for x, s in zip(xs, states):
    ax.text(x, 0.55, s, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.35", fill=False))
for a, b in zip(xs[:4], xs[1:5]):
    ax.annotate("", xy=(b-0.06,0.55), xytext=(a+0.06,0.55), arrowprops=dict(arrowstyle="->"))
ax.annotate("", xy=(0.84,0.50), xytext=(0.62,0.42), arrowprops=dict(arrowstyle="->", linestyle="dashed"))
ax.text(0.5,0.12,"Pre-boundary non-emission remains outside completeness",ha="center")
ax.set_title("Emission state machine")
save("figure_04_emission_state_machine")
