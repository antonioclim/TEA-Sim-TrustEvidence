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
cell_text = [
 ["TrustEvidence field", "FHIR/BALP mapping status"],
 ["event / actor / source", "AuditEvent / BALP-compatible"],
 ["payload commitment", "EvidenceAnchor extension"],
 ["provenance assertion", "Provenance profile"],
 ["verifier capability", "CapabilityStatement"],
 ["QA status", "QA required before conformance claims"]]
tab = ax.table(cellText=cell_text[1:], colLabels=cell_text[0], loc="center", cellLoc="left")
tab.auto_set_font_size(False); tab.set_fontsize(9); tab.scale(1,1.6)
ax.set_title("Draft FHIR/BALP mapping")
save("figure_07_ig_mapping")
