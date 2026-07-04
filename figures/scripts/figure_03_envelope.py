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

fig, ax = plt.subplots(figsize=(7,4))
ax.axis("off")
blocks = [("Artefact core\n(signed)",0.5,0.75),("Emitter signature",0.5,0.55),("Backend receipt\n(outside signed core)",0.5,0.35),("Verification material\n(optional)",0.5,0.15)]
for text, x, y in blocks:
    ax.text(x, y, text, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.4", fill=False))
ax.annotate("", xy=(0.5,0.63), xytext=(0.5,0.67), arrowprops=dict(arrowstyle="->"))
ax.annotate("", xy=(0.5,0.43), xytext=(0.5,0.47), arrowprops=dict(arrowstyle="->"))
ax.annotate("", xy=(0.5,0.23), xytext=(0.5,0.27), arrowprops=dict(arrowstyle="->"))
ax.set_title("TrustEvidence envelope decomposition")
save("figure_03_envelope")
