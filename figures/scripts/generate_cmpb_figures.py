from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
import os
import textwrap
from pathlib import Path

os.environ.setdefault('SOURCE_DATE_EPOCH', '0')
os.environ.setdefault('MPLBACKEND', 'Agg')

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

mpl.rcParams['svg.hashsalt'] = 'teasim-cmpb-figures-v1'
mpl.rcParams['pdf.compression'] = 6
mpl.rcParams['font.family'] = 'DejaVu Sans'

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'figures' / 'sources'
OUTPUT = ROOT / 'figures' / 'outputs'
OUTPUT.mkdir(parents=True, exist_ok=True)

EPOCH = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)


def read_csv(name: str) -> list[dict[str, str]]:
    with (SOURCE / name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def save_figure(fig: plt.Figure, stem: str, title: str, description: str) -> None:
    pdf_meta = {
        'Title': title,
        'Author': 'TEA-Sim v2.1.0',
        'Subject': description,
        'Keywords': 'personal health monitoring, audit evidence, reproducibility',
        'Creator': 'Matplotlib 3.10.8; TEA-Sim deterministic figure generator',
        'Producer': 'Matplotlib pdf backend',
        'CreationDate': EPOCH,
        'ModDate': EPOCH,
    }
    svg_meta = {
        'Title': title,
        'Description': description,
        'Creator': 'Matplotlib 3.10.8; TEA-Sim deterministic figure generator',
        'Date': '1970-01-01T00:00:00Z',
        'Keywords': ['personal health monitoring', 'audit evidence', 'reproducibility'],
    }
    png_meta = {
        'Title': title,
        'Description': description,
        'Software': 'Matplotlib 3.10.8; TEA-Sim deterministic figure generator',
    }
    fig.savefig(OUTPUT / f'{stem}.pdf', metadata=pdf_meta)
    svg_path = OUTPUT / f'{stem}.svg'
    fig.savefig(svg_path, metadata=svg_meta)
    # Matplotlib may emit trailing spaces in SVG path-data lines. Strip them
    # so that `git diff --check` remains clean and Git round-trips preserve
    # the exact release bytes. This transformation is deterministic.
    svg_text = svg_path.read_text(encoding='utf-8')
    svg_path.write_text(
        '\n'.join(line.rstrip() for line in svg_text.splitlines()) + '\n',
        encoding='utf-8',
        newline='\n',
    )
    fig.savefig(OUTPUT / f'{stem}.png', dpi=600, metadata=png_meta)
    plt.close(fig)


def draw_box(ax, row: dict[str, str], title_size: float = 8.7, subtitle_size: float = 6.1) -> None:
    x, y = float(row['x']), float(row['y'])
    w, h = float(row['width']), float(row['height'])
    ax.add_patch(Rectangle((x, y), w, h, fill=False, linewidth=1.15))
    label = row.get('label') or row.get('stage') or ''
    subtitle = row.get('subtitle') or row.get('operation') or ''
    title_wrap = max(9, int(w * 10.5))
    subtitle_wrap = max(10, int(w * 12))
    label = textwrap.fill(label, width=title_wrap)
    subtitle = textwrap.fill(subtitle, width=subtitle_wrap)
    ax.text(x + w / 2, y + h * 0.65, label, ha='center', va='center', fontsize=title_size, fontweight='bold', linespacing=0.95)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.21, subtitle, ha='center', va='center', fontsize=subtitle_size, linespacing=0.95)


def node_map(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r['id']: r for r in rows}


def box_anchor(row: dict[str, str], side: str) -> tuple[float, float]:
    x, y, w, h = map(float, [row['x'], row['y'], row['width'], row['height']])
    return {
        'left': (x, y + h / 2),
        'right': (x + w, y + h / 2),
        'top': (x + w / 2, y + h),
        'bottom': (x + w / 2, y),
        'centre': (x + w / 2, y + h / 2),
    }[side]


def arrow(ax, start, end, label: str = '', dashed: bool = False, rad: float = 0.0, label_offset=(0.0, 0.0)) -> None:
    patch = FancyArrowPatch(
        start, end,
        arrowstyle='-|>',
        mutation_scale=11,
        linewidth=1.0,
        linestyle='--' if dashed else '-',
        connectionstyle=f'arc3,rad={rad}',
        shrinkA=2,
        shrinkB=2,
    )
    ax.add_patch(patch)
    if label:
        mx = (start[0] + end[0]) / 2 + label_offset[0]
        my = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(mx, my, label, ha='center', va='center', fontsize=7.2)


def generate_figure_1() -> None:
    nodes = read_csv('figure1_nodes.csv')
    edges = read_csv('figure1_edges.csv')
    nm = node_map(nodes)
    fig = plt.figure(figsize=(7.2, 4.3))
    ax = fig.add_axes([0.02, 0.04, 0.96, 0.90])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title('Schema-first curation boundary', fontsize=13, fontweight='bold', pad=8)
    ax.plot([0.25, 9.85], [3.65, 3.65], linewidth=0.9, linestyle='--')
    ax.text(0.28, 5.75, 'Governed payload path', fontsize=9.0, fontweight='bold', va='top')
    ax.text(0.28, 3.48, 'Curated audit-evidence path', fontsize=9.0, fontweight='bold', va='top')
    for r in nodes:
        draw_box(ax, r)
    for e in edges:
        s, t = nm[e['source']], nm[e['target']]
        if e['source'] == 'payload' and e['target'] == 'clinical_store':
            start, end = box_anchor(s, 'right'), box_anchor(t, 'left')
            arrow(ax, start, end, e['label'], False, label_offset=(0, 0.18))
        elif e['source'] == 'payload' and e['target'] == 'detect':
            start, end = box_anchor(s, 'bottom'), box_anchor(t, 'top')
            arrow(ax, start, end, e['label'], True, rad=0.0, label_offset=(0.64, 0.0))
        elif e['source'] == 'append' and e['target'] == 'preserve':
            start, end = box_anchor(s, 'bottom'), box_anchor(t, 'top')
            arrow(ax, start, end)
        else:
            start, end = box_anchor(s, 'right'), box_anchor(t, 'left')
            arrow(ax, start, end)
    ax.text(0.40, 0.30, 'Boundary rule: raw physiological values and samples do not enter the public evidence envelope.', fontsize=7.8)
    save_figure(fig, 'Figure_1', 'Schema-first curation boundary', 'Separation of governed monitoring payloads from the curated audit-evidence pathway.')


def generate_figure_2() -> None:
    rows = read_csv('figure2_components.csv')
    sections: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        sections.setdefault(r['section'], []).append(r)
    for vals in sections.values():
        vals.sort(key=lambda x: int(x['order']))
    fig = plt.figure(figsize=(7.2, 5.0))
    ax = fig.add_axes([0.02, 0.04, 0.96, 0.90])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title('Evidence envelope and payload minimisation', fontsize=13, fontweight='bold', pad=8)

    ax.add_patch(Rectangle((0.35, 0.45), 5.05, 5.15, fill=False, linewidth=1.35))
    ax.text(0.50, 5.47, 'TrustEvidenceEnvelope', fontsize=10.5, fontweight='bold', va='top')
    ax.add_patch(Rectangle((0.62, 2.05), 4.51, 3.10, fill=False, linewidth=1.05))
    ax.text(0.78, 4.98, 'evidence_core (signed)', fontsize=9.4, fontweight='bold', va='top')
    core = sections['evidence_core']
    columns = [(0.82, core[:3]), (3.03, core[3:])]
    for x0, items in columns:
        y0 = 4.52
        for r in items:
            ax.text(x0, y0, r['component'], fontsize=7.6, fontweight='bold', va='top')
            ax.text(x0, y0 - 0.22, textwrap.fill(r['details'], 31), fontsize=6.8, va='top', linespacing=1.05)
            y0 -= 0.83

    ax.add_patch(Rectangle((0.62, 0.70), 4.51, 1.05, fill=False, linewidth=1.05))
    ax.text(0.78, 1.60, 'backend_receipt (signed)', fontsize=9.2, fontweight='bold', va='top')
    receipt_x = [0.82, 2.22, 3.66]
    for x0, r in zip(receipt_x, sections['backend_receipt']):
        ax.text(x0, 1.28, r['component'], fontsize=7.0, fontweight='bold', va='top')
        ax.text(x0, 1.05, textwrap.fill(r['details'], 22), fontsize=6.35, va='top', linespacing=1.0)

    boxes = [
        ('Retained accountability content', sections['retained'], 5.75, 4.17, 3.85, 1.25),
        ('Excluded from public envelope', sections['excluded'], 5.75, 2.20, 3.85, 1.55),
        ('Withheld authorised side', sections['withheld'], 5.75, 0.45, 3.85, 1.30),
    ]
    for title, vals, x, y0, w, h in boxes:
        ax.add_patch(Rectangle((x, y0), w, h, fill=False, linewidth=1.05))
        ax.text(x + 0.18, y0 + h - 0.18, title, fontsize=9.0, fontweight='bold', va='top')
        yy = y0 + h - 0.55
        for r in vals:
            wrapped = textwrap.fill(r['details'], width=43)
            ax.text(x + 0.20, yy, '- ' + wrapped, fontsize=7.0, va='top', linespacing=1.05)
            yy -= 0.47 if '\n' in wrapped else 0.32

    ax.text(5.85, 1.86, 'Commitment check uses withheld payload + nonce.', fontsize=6.9)
    ax.text(0.40, 0.14, 'Binding is not encryption or anonymisation; source truth and clinical validity are outside this envelope.', fontsize=7.6)
    save_figure(fig, 'Figure_2', 'Evidence envelope and payload minimisation', 'Schema-derived envelope structure with retained, excluded, and withheld content boundaries.')


def generate_figure_3() -> None:
    stages = read_csv('figure3_stages.csv')
    edges = read_csv('figure3_edges.csv')
    nm = node_map(stages)
    fig = plt.figure(figsize=(7.2, 5.0))
    ax = fig.add_axes([0.02, 0.04, 0.96, 0.90])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title('Execution and verification pipeline', fontsize=13, fontweight='bold', pad=8)
    for r in stages:
        draw_box(ax, r, title_size=7.6, subtitle_size=5.0)
    for e in edges:
        s, t = nm[e['source']], nm[e['target']]
        if e['source'] == 'sign_core' and e['target'] == 'append':
            arrow(ax, box_anchor(s, 'bottom'), box_anchor(t, 'top'))
        elif int(s['row']) == 1:
            arrow(ax, box_anchor(s, 'right'), box_anchor(t, 'left'))
        else:
            arrow(ax, box_anchor(s, 'left'), box_anchor(t, 'right'))
    ax.text(0.40, 5.55, 'Creation path', fontsize=9.1, fontweight='bold')
    ax.text(0.40, 3.05, 'Receipt verification and preservation path', fontsize=9.1, fontweight='bold')
    ax.text(0.40, 0.48, 'Failure classes: minimisation; schema/semantics; time; canonicalisation; signatures; proof/consistency; checkpoint; archive.', fontsize=7.2)
    ax.text(0.40, 0.19, 'Later cryptographic checks do not replace earlier schema, semantic or payload-minimisation checks.', fontsize=7.2)
    save_figure(fig, 'Figure_3', 'Execution and verification pipeline', 'Implemented pipeline from minimisation and validation to local receipt verification and checkpoint preservation.')


def generate_figure_4() -> None:
    rows = read_csv('figure4_passage_results.csv')
    x = list(range(len(rows)))
    receipt = [int(r['receipt_bytes_median']) for r in rows]
    proof = [int(r['proof_bytes_median']) for r in rows]
    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    ax.plot(x, receipt, marker='o', linewidth=1.4, label='Median signed receipt')
    ax.plot(x, proof, marker='s', linewidth=1.4, label='Median inclusion proof')
    labels = [
        f"{r['descriptor_id']}\n{int(r['tree_size']):,} leaves\npath depth {r['expected_authentication_path_depth']}"
        for r in rows
    ]
    ax.set_xticks(x, labels)
    ax.set_ylabel('Canonical serialised size (bytes)')
    ax.set_title('Bounded local passage and receipt sizes', fontsize=13, fontweight='bold', pad=10)
    ax.grid(axis='y', linewidth=0.5)
    ax.legend(loc='upper left', fontsize=7.7, frameon=False)
    ax.set_ylim(480, 1760)
    for series, offset in ((receipt, 8), (proof, 8)):
        for xi, yi in zip(x, series):
            ax.annotate(f'{yi:,}', (xi, yi), textcoords='offset points', xytext=(0, offset),
                        ha='center', fontsize=7.4)
    total_events = sum(int(r['event_count']) for r in rows)
    receipt_checks = sum(int(r['successful_receipt_checks']) for r in rows)
    mutation_cases = sum(int(r['mutation_cases']) for r in rows)
    mutation_rejections = sum(int(r['mutation_rejections']) for r in rows)
    validation_failures = sum(int(r['validation_failures']) for r in rows)
    ordinary_failures = sum(int(r['ordinary_verification_failures']) for r in rows)
    record_lines = [
        'Executed integrated reference run:',
        f'{total_events:,} synthetic events',
        f'{receipt_checks:,} sampled receipt checks',
        f'{mutation_rejections}/{mutation_cases} re-signed proof mutations rejected',
        f'{validation_failures} validation failures; {ordinary_failures} ordinary verification failures',
    ]
    ax.text(0.03, 0.43, '\n'.join(record_lines), transform=ax.transAxes, va='top', fontsize=7.1,
            bbox={'boxstyle':'round,pad=0.42', 'fill':False})
    fig.text(0.12, 0.025,
             'Timings are single-host descriptive measurements; this is not a comparative or production benchmark.',
             fontsize=7.0)
    fig.subplots_adjust(left=0.12, right=0.955, bottom=0.26, top=0.86)
    save_figure(fig, 'Figure_4', 'Bounded local passage and receipt sizes',
                'Executed synthetic passage at 128, 512 and 2,048 leaves with serialised receipt and proof sizes.')


def generate_figure_5() -> None:
    rows = read_csv('figure5_failure_modes.csv')
    rows = list(reversed(rows))
    y = list(range(len(rows)))
    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    groups = [
        (2, 'o'),
        (1, 's'),
        (0, 'x'),
    ]
    for code, marker in groups:
        xs = [int(r['status_code']) for r in rows if int(r['status_code']) == code]
        ys = [i for i, r in enumerate(rows) if int(r['status_code']) == code]
        ax.scatter(xs, ys, marker=marker, s=42)
    for i, r in enumerate(rows):
        code = int(r['status_code'])
        ax.hlines(i, 0, code, linewidth=0.7, linestyle=':')
        ax.text(2.10, i, r['evidence'], va='center', fontsize=6.6)
    ax.set_yticks(y, [textwrap.fill(r['failure_mode'], 31) for r in rows], fontsize=7.4)
    ax.set_xticks([0, 1, 2], ['outside scope', 'bounded / partial', 'executed control'])
    ax.set_xlim(-0.15, 3.15)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_title('Failure modes addressed and not addressed', fontsize=13, fontweight='bold', pad=10)
    ax.grid(axis='x', linewidth=0.5)
    fig.text(0.34, 0.035, 'Markers: x = outside scope; square = bounded/partial; circle = executed control.', fontsize=6.8)
    fig.text(0.34, 0.014, 'Executed control does not imply exhaustive security, clinical validity or global non-equivocation.', fontsize=6.8)
    fig.subplots_adjust(left=0.33, right=0.985, bottom=0.18, top=0.90)
    save_figure(fig, 'Figure_5', 'Failure modes addressed and not addressed', 'Executed controls, bounded limitations, and explicitly out-of-scope failure modes.')


def main() -> None:
    for p in OUTPUT.glob('Figure_*.*'):
        p.unlink()
    generate_figure_1()
    generate_figure_2()
    generate_figure_3()
    generate_figure_4()
    generate_figure_5()
    summary = {
        'generator': 'figures/scripts/generate_cmpb_figures.py',
        'software': {'matplotlib': mpl.__version__},
        'figures': [],
    }
    for stem in [f'Figure_{i}' for i in range(1, 6)]:
        row = {'figure': stem}
        for ext in ['pdf', 'png', 'svg']:
            p = OUTPUT / f'{stem}.{ext}'
            row[ext] = {'bytes': p.stat().st_size, 'sha256': sha256(p)}
        summary['figures'].append(row)
    (OUTPUT / 'figure_build_summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
