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
rows = ["Tamper-evidence", "Append-only", "Inclusion", "Non-equivocation", "Freshness"]
cols = ["A1 central", "A2 hash log", "A3 ledger-like"]
vals = [["assumption-bound", "fails", "fails"], ["fails", "assumption-bound", "assumption-bound"], ["fails", "assumption-bound", "assumption-bound"], ["fails", "A7 only", "A8 only"], ["assumption-bound", "assumption-bound", "assumption-bound"]]
cell_text = [[r] + v for r, v in zip(rows, vals)]
tab = ax.table(cellText=cell_text, colLabels=["Property"] + cols, loc="center", cellLoc="center")
tab.auto_set_font_size(False); tab.set_fontsize(9); tab.scale(1, 1.5)
ax.set_title("Property-backend matrix; production guarantee not asserted")
save("figure_02_property_matrix")
