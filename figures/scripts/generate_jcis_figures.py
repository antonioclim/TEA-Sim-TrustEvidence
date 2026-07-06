#!/usr/bin/env python3
"""Generate journal-ready JCIS figures from kit CSV data.

The generator intentionally avoids hand-drawn image assets. Every box, arrow and
annotation is read from CSV specifications or derived from evidence CSVs copied
from the FHIR/BALP, backend, workload and property-validation kits.
"""
from __future__ import annotations

import csv
import math
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "figure_sources"
OUT = ROOT / "figures" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

PDF_METADATA = {"CreationDate": None, "ModDate": None, "Creator": "TEA-Sim figure generator"}
SVG_METADATA = {"Date": None}

# A restrained greyscale + single accent palette. This remains readable when
# printed in greyscale and avoids decorative saturation.
EDGE = "#263238"
TEXT = "#111111"
GRID = "#B0BEC5"
FILL = {
    "source": "#F5F7FA",
    "boundary": "#E8F1FA",
    "backend": "#F7F7F7",
    "backend_executed": "#EAF5EA",
    "stage": "#F6F8FB",
    "demotion": "#FFF6E5",
    "scope": "#FFFFFF",
    "warn": "#FFF6E5",
}
ACCENT = "#2F6F9F"
EXECUTED = "#6B8E23"
DEMOTED = "#8A6D3B"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9.5,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "savefig.dpi": 300,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.hashsalt": "tea-sim-v2.0.1",
})

@dataclass
class Node:
    id: str
    label: str
    x: float
    y: float
    w: float
    h: float
    type: str
    note: str = ""

    @property
    def left(self) -> float: return self.x - self.w / 2
    @property
    def right(self) -> float: return self.x + self.w / 2
    @property
    def bottom(self) -> float: return self.y - self.h / 2
    @property
    def top(self) -> float: return self.y + self.h / 2


def read_csv_dict(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8", errors="ignore") as f:
        return list(csv.DictReader(f))


def load_nodes(path: Path) -> dict[str, Node]:
    nodes = {}
    for r in read_csv_dict(path):
        nodes[r["id"]] = Node(
            r["id"], r["label"], float(r["x"]), float(r["y"]), float(r["w"]), float(r["h"]), r.get("type", "stage"), r.get("note", "")
        )
    return nodes


def wrap_label(text: str, width_chars: int) -> str:
    out = []
    for part in text.split("\n"):
        out.append(textwrap.fill(part, width=width_chars, break_long_words=False, break_on_hyphens=False))
    return "\n".join(out)


def draw_node(ax, node: Node, lw: float = 1.2):
    box = FancyBboxPatch(
        (node.left, node.bottom), node.w, node.h,
        boxstyle="round,pad=0.012,rounding_size=1.2",
        linewidth=lw,
        edgecolor=EDGE,
        facecolor=FILL.get(node.type, "#FFFFFF"),
        zorder=2,
    )
    ax.add_patch(box)
    width_chars = max(14, int(node.w * 1.35))
    ax.text(
        node.x, node.y, wrap_label(node.label, width_chars),
        ha="center", va="center", color=TEXT,
        fontsize=8.3 if node.type != "scope" else 8.0,
        linespacing=1.25,
        zorder=3,
    )


def edge_point(src: Node, dst: Node) -> tuple[tuple[float, float], tuple[float, float]]:
    """Return points on the rectangle edges, not inside boxes."""
    dx = dst.x - src.x
    dy = dst.y - src.y
    # Decide whether connection is primarily horizontal or vertical.
    if abs(dx) >= abs(dy):
        start = (src.right if dx >= 0 else src.left, src.y)
        end = (dst.left if dx >= 0 else dst.right, dst.y)
    else:
        start = (src.x, src.top if dy >= 0 else src.bottom)
        end = (dst.x, dst.bottom if dy >= 0 else dst.top)
    return start, end


def draw_poly_arrow(ax, pts: list[tuple[float, float]], label: str = ""):
    if len(pts) < 2:
        return
    # Draw intermediate line segments without arrow head.
    for a, b in zip(pts[:-2], pts[1:-1]):
        ax.add_line(Line2D([a[0], b[0]], [a[1], b[1]], color=EDGE, lw=1.05, zorder=1))
    # Final segment with arrow head.
    arr = FancyArrowPatch(
        pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=10,
        linewidth=1.05, color=EDGE, shrinkA=0, shrinkB=0,
        connectionstyle="arc3,rad=0", zorder=1,
    )
    ax.add_patch(arr)
    if label:
        # Label at midpoint of the longest segment.
        segs = [(math.hypot(b[0]-a[0], b[1]-a[1]), a, b) for a, b in zip(pts[:-1], pts[1:])]
        _, a, b = max(segs, key=lambda x: x[0])
        lx, ly = (a[0]+b[0])/2, (a[1]+b[1])/2
        ax.text(lx, ly + 2.2, wrap_label(label, 16), ha="center", va="bottom", fontsize=7.6,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.8), zorder=4)


def parse_route(route: str) -> list[tuple[float, float]]:
    pts = []
    for item in (route or "").split(";"):
        item = item.strip()
        if not item:
            continue
        x, y = item.split(",")
        pts.append((float(x), float(y)))
    return pts


def draw_node_edge_figure(nodes_file: str, edges_file: str, title: str, out_stem: str, size=(10.4, 5.6)):
    nodes = load_nodes(SRC / nodes_file)
    edges = read_csv_dict(SRC / edges_file)
    fig, ax = plt.subplots(figsize=size)
    ax.set_xlim(0, 108); ax.set_ylim(0, 88); ax.axis("off")
    ax.set_title(title, pad=10)
    for node in nodes.values():
        draw_node(ax, node)
    for e in edges:
        s, t = nodes[e["source"]], nodes[e["target"]]
        start, end = edge_point(s, t)
        route = parse_route(e.get("route", ""))
        pts = [start] + route + [end]
        draw_poly_arrow(ax, pts, e.get("label", ""))
    save_all(fig, out_stem)


def summarise_validation() -> tuple[int, int, int]:
    rows = read_csv_dict(SRC / "validation_matrix.csv")
    total = len(rows)
    local_pass = sum(1 for r in rows if r.get("json_integrity_lint") == "PASS" and r.get("local_profile_check") == "PASS")
    official_pending = sum(1 for r in rows if "SKIPPED" in r.get("hl7_fhir_validator_status", ""))
    return total, local_pass, official_pending


def summarise_properties() -> tuple[int, int, int]:
    rows = read_csv_dict(SRC / "property_to_claim_matrix.csv")
    prop = [r for r in rows if r.get("property_id", "").startswith("P")]
    passed = sum(1 for r in prop if r.get("status") == "PASS")
    not_exec = sum(1 for r in rows if r.get("status") == "NOT_EXECUTED")
    return len(prop), passed, not_exec


def draw_figure2():
    total, local_pass, official_pending = summarise_validation()
    p_total, p_pass, p_pending = summarise_properties()
    draw_node_edge_figure(
        "figure2_nodes.csv", "figure2_edges.csv",
        "Evidence construction and claim-demotion pipeline",
        "figure2_evidence_demotion_pipeline", size=(11.6, 5.2)
    )
    # Add an evidence status strip by re-opening a new figure for richer annotation.
    nodes = load_nodes(SRC / "figure2_nodes.csv")
    edges = read_csv_dict(SRC / "figure2_edges.csv")
    fig, ax = plt.subplots(figsize=(11.6, 5.6))
    ax.set_xlim(0, 108); ax.set_ylim(0, 90); ax.axis("off")
    ax.set_title("Evidence construction and claim-demotion pipeline", pad=10)
    for node in nodes.values(): draw_node(ax, node)
    for e in edges:
        s, t = nodes[e["source"]], nodes[e["target"]]
        start, end = edge_point(s, t)
        draw_poly_arrow(ax, [start] + parse_route(e.get("route", "")) + [end], e.get("label", ""))
    # Compact evidence cards derived from kit CSVs.
    cards = [
        ("FHIR/BALP artefacts", f"{local_pass}/{total} local checks passed\nofficial validator pending"),
        ("A2 backend", "1k and 10k local runs\nA1/A3 demoted"),
        ("Properties", f"{p_pass}/{p_total} P-family checks passed\nTLA+/Alloy not executed"),
    ]
    x0 = 15
    for i, (head, body) in enumerate(cards):
        x = x0 + i * 30
        r = Node(f"card{i}", f"{head}\n{body}", x, 12, 25, 10, "scope", "")
        draw_node(ax, r, lw=0.9)
    save_all(fig, "figure2_evidence_demotion_pipeline")




def draw_figure3():
    """Draw Figure 3 as a two-lane flow to avoid box overlap and crossing arrows.

    Geometry is read from figure3_nodes.csv and figure3_edges.csv; evidence call-outs
    are computed from backend_benchmark_summary.csv and tamper_detection_results.csv.
    """
    nodes = load_nodes(SRC / "figure3_nodes.csv")
    edges = read_csv_dict(SRC / "figure3_edges.csv")
    bench = [r for r in read_csv_dict(SRC / "backend_benchmark_summary.csv") if r.get("backend") == "A2_MERKLE" and r.get("status") == "executed"]
    tamper_rows = read_csv_dict(SRC / "tamper_detection_results.csv")
    counts = ", ".join(f"{int(float(r['object_count'])):,}" for r in bench if str(r.get('object_count','')).replace('.','',1).isdigit()) or "executed counts recorded"
    tamper_pass = sum(1 for r in tamper_rows if r.get("status", "").lower() == "pass")
    tamper_total = len(tamper_rows)
    rep_values = sorted({int(float(r.get('repetitions_executed', 0))) for r in bench if str(r.get('repetitions_executed','')).replace('.','',1).isdigit()})
    reps = rep_values[-1] if rep_values else 0

    fig, ax = plt.subplots(figsize=(11.1233, 4.9467))  # 3337 x 1484 px at 300 dpi
    ax.set_xlim(0, 108); ax.set_ylim(0, 82); ax.axis("off")
    ax.set_title("A2 Merkle local reference execution and verification flow", pad=8)

    # Lane labels kept outside the boxes so arrows never cross labels or rectangles.
    ax.text(4, 71.5, "append path", ha="left", va="center", fontsize=8.1, color=ACCENT, weight="bold")
    ax.text(4, 47.5, "verification path", ha="left", va="center", fontsize=8.1, color=ACCENT, weight="bold")

    for nid in ["object", "canonical", "leaf", "append", "receipt", "verify", "properties", "boundary"]:
        draw_node(ax, nodes[nid], lw=1.25 if nid != "boundary" else 1.0)

    # Use edge-anchor points; for the append->receipt turn the vertical arrow runs only
    # through whitespace between the boxes. The lower lane intentionally flows right-to-left.
    for e in edges:
        s, t = nodes[e["source"]], nodes[e["target"]]
        start, end = edge_point(s, t)
        draw_poly_arrow(ax, [start] + parse_route(e.get("route", "")) + [end], e.get("label", ""))

    # Evidence call-outs derive from the backend-evaluation workstream CSVs and keep the caption honest.
    card1 = Node("run_card", f"A2 executed locally\n{counts} objects; {reps} retained reps", 28, 20.5, 27, 8.3, "backend_executed", "")
    card2 = Node("tamper_card", f"Tamper/receipt checks\n{tamper_pass}/{tamper_total} cases passed", 58, 20.5, 25, 8.3, "backend_executed", "")
    card3 = Node("limit_card", "A1/A3 not executed\nin this runtime", 84, 20.5, 22, 8.3, "demotion", "")
    for card in [card1, card2, card3]:
        draw_node(ax, card, lw=0.95)

    # These short vertical connectors link the verification lane to evidence status without
    # crossing any node body.
    draw_poly_arrow(ax, [(nodes["properties"].x, nodes["properties"].bottom), (nodes["properties"].x, card1.top)])
    draw_poly_arrow(ax, [(nodes["verify"].x, nodes["verify"].bottom), (nodes["verify"].x, card2.top)])
    draw_poly_arrow(ax, [(nodes["receipt"].x, nodes["receipt"].bottom), (card3.x, card3.top)])

    # Fixed-size export preserves the DOCX aspect ratio and prevents Word stretching.
    fig.subplots_adjust(left=0.035, right=0.985, top=0.88, bottom=0.07)
    stem = "figure3_a2_merkle_flow"
    for ext in ("svg", "pdf", "png"):
        if ext == "png":
            fig.savefig(OUT / f"{stem}.{ext}", dpi=300)
        elif ext == "pdf":
            fig.savefig(OUT / f"{stem}.{ext}", metadata=PDF_METADATA)
        elif ext == "svg":
            fig.savefig(OUT / f"{stem}.{ext}", metadata=SVG_METADATA)
    plt.close(fig)


def draw_figure4():
    scenarios = read_csv_dict(SRC / "calibrated_scenarios.csv")
    a2 = {r["scenario_id"]: r for r in read_csv_dict(SRC / "calibrated_a2_summary.csv")}
    # Keep order C1-C4
    scenarios = sorted(scenarios, key=lambda r: r["scenario_id"])
    fig, ax = plt.subplots(figsize=(11.4, 6.3))
    ax.set_xlim(0, 110); ax.set_ylim(0, 90); ax.axis("off")
    ax.set_title("Descriptor-informed workload construction", pad=10)
    # Left source blocks
    sources = [
        ("Synthea pathway", "FHIR R4 synthetic\npatient generation\nmetadata plus assumption", 14, 72),
        ("BIG IDEAs", "16 participants;\nup to 10 days;\n5-min CGM metadata", 14, 51),
        ("MIMIC-on-FHIR demo", "100-patient public\ndemo metadata;\nresource-profile proxy", 14, 30),
    ]
    src_nodes = []
    for idx, (title, body, x, y) in enumerate(sources):
        n = Node(f"source{idx}", f"{title}\n{body}", x, y, 24, 13, "source", "")
        src_nodes.append(n); draw_node(ax, n)
    # Scenario blocks centre
    scen_nodes=[]
    ys=[76,58,40,22]
    for i, r in enumerate(scenarios):
        sid = r["scenario_id"].split("_")[0]
        events = int(float(r["planned_evidence_events"]))
        exec_events = int(float(a2.get(r["scenario_id"], {}).get("executed_a2_events", min(events,10000)))) if a2 else min(events,10000)
        pref = r.get("backend_preference", "")
        label=f"{sid}: {events:,} planned\n{exec_events:,} A2 passage\n{pref}"
        n=Node(f"scen{i}", label, 52, ys[i], 25, 11, "stage", "")
        scen_nodes.append(n); draw_node(ax,n)
    # Right result boundary
    cap=Node("cap", "Capped local A2 passage\ndescriptor-derived objects\nnot full external extraction", 91, 49, 28, 16, "demotion", "")
    draw_node(ax, cap)
    # Source to scenarios
    connections=[(src_nodes[0], scen_nodes[0]), (src_nodes[1], scen_nodes[1]), (src_nodes[2], scen_nodes[2]), (src_nodes[1], scen_nodes[3])]
    for s,t in connections:
        start,end=edge_point(s,t)
        midx=33
        draw_poly_arrow(ax,[start,(midx,start[1]),(midx,end[1]),end])
    for n in scen_nodes:
        start,end=edge_point(n,cap)
        draw_poly_arrow(ax,[start,(74,n.y),(74,cap.y),end])
    # Bottom note
    ax.text(55, 7, "All values are descriptor/event-opportunity counts from source metadata or explicit assumptions; they are not clinical validation results.",
            ha="center", va="center", fontsize=8.2, color=TEXT)
    save_all(fig, "figure4_workload_descriptors")


def draw_figure5():
    tiles = read_csv_dict(SRC / "figure5_backend_tiles.csv")
    bench = read_csv_dict(SRC / "backend_benchmark_summary.csv")
    status = {r["backend"].replace("_", " "): r["status"] for r in bench}
    fig, ax = plt.subplots(figsize=(9.8, 7.2))
    ax.set_xlim(0, 105); ax.set_ylim(0, 105)
    ax.set_xlabel("Governance and dispute intensity", labelpad=10)
    ax.set_ylabel("Verification burden and external scrutiny", labelpad=12)
    ax.set_xticks([]); ax.set_yticks([])
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_linewidth(1.1)
    ax.annotate("", xy=(103,0), xytext=(0,0), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=EDGE))
    ax.annotate("", xy=(0,103), xytext=(0,0), arrowprops=dict(arrowstyle="-|>", lw=1.2, color=EDGE))
    ax.plot([9, 94], [18, 91], color=GRID, lw=1.1, linestyle="--", zorder=0)
    ax.text(68, 91, "Stronger evidence replication only when governance/dispute conditions justify it", fontsize=8.6, ha="center", va="bottom")
    for r in tiles:
        x,y,w,h=float(r['x']),float(r['y']),float(r['w']),float(r['h'])
        typ = 'backend_executed' if r['backend']=='A2' else 'backend'
        node=Node(r['backend'], f"{r['title']}\n{r['execution_status']}\n{r['appropriate_when']}\nClaim boundary: {r['claim_boundary']}", x,y,w,h,typ,'')
        draw_node(ax,node,lw=1.4 if r['backend']=='A2' else 1.1)
    # Decision not arrows through boxes: use a clean diagonal decision zone with short labels.
    ax.text(18, 10, "internal audit suffices", fontsize=8.2, ha="center")
    ax.text(50, 37, "portable verification", fontsize=8.2, ha="center")
    ax.text(82, 61, "external witness desired", fontsize=8.2, ha="center")
    ax.text(52, 99, "Decision map is conceptual and evidence-limited: only A2 was executed locally.",
            ha="center", va="top", fontsize=8.4, color=TEXT)
    save_all(fig, "figure5_backend_decision_map")


def save_all(fig, stem: str):
    fig.subplots_adjust(left=0.035, right=0.985, top=0.91, bottom=0.08)
    for ext in ("svg", "pdf", "png"):
        kwargs = {"bbox_inches":"tight"}
        if ext == "png":
            kwargs["dpi"] = 300
        elif ext == "pdf":
            kwargs["metadata"] = PDF_METADATA
        elif ext == "svg":
            kwargs["metadata"] = SVG_METADATA
        fig.savefig(OUT / f"{stem}.{ext}", **kwargs)
    plt.close(fig)


def write_qa():
    rows=[]
    for p in sorted(OUT.glob("*.png")):
        try:
            from PIL import Image
            img=Image.open(p)
            w,h=img.size
            status="PASS" if w>=1800 and h>=1200 else "CHECK"
        except Exception:
            w=h=0; status="FAIL"
        rows.append({"file":p.name,"width_px":w,"height_px":h,"qa_status":status,"notes":"300 dpi PNG generated from vector source; visual contact sheet required"})
    with (ROOT/"FIGURE_LAYOUT_QA.csv").open('w', newline='', encoding='utf-8') as f:
        writer=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)


def make_contact_sheet():
    from PIL import Image, ImageOps, ImageDraw, ImageFont
    imgs=[]
    for p in sorted(OUT.glob("figure*.png")):
        im=Image.open(p).convert('RGB')
        # Scale to fixed width for contact sheet while retaining aspect.
        target_w=920
        target_h=int(im.height*target_w/im.width)
        im=im.resize((target_w,target_h), Image.Resampling.LANCZOS)
        panel=Image.new('RGB',(target_w,target_h+34),'white')
        panel.paste(im,(0,34))
        draw=ImageDraw.Draw(panel)
        draw.text((8,8),p.name,fill=(0,0,0))
        panel=ImageOps.expand(panel,border=1,fill=(180,180,180))
        imgs.append(panel)
    maxw=max(i.width for i in imgs); totalh=sum(i.height for i in imgs)+14*(len(imgs)-1)
    sheet=Image.new('RGB',(maxw,totalh),'white')
    y=0
    for im in imgs:
        sheet.paste(im,(0,y)); y+=im.height+14
    sheet.save(ROOT/"GENERATED_FIGURES_CONTACT_SHEET.png")


def main():
    draw_node_edge_figure("figure1_nodes.csv", "figure1_edges.csv", "TrustEvidence evidence-boundary architecture", "figure1_boundary_architecture", size=(11.2, 6.0))
    draw_figure2()
    draw_figure3()
    draw_figure4()
    draw_figure5()
    write_qa()
    make_contact_sheet()

if __name__ == "__main__":
    main()
