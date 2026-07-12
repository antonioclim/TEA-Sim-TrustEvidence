from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tables' / 'sources'
OUTPUT = ROOT / 'tables' / 'outputs'
OUTPUT.mkdir(parents=True, exist_ok=True)

TABLES = [
    ('Table 1. Curation problem decomposition', 'Table_1_curation_problem_decomposition.csv',
     'The stages distinguish monitoring-accountability curation from the governed physiological-payload pathway.'),
    ('Table 2. TrustEvidence envelope specification', 'Table_2_envelope_specification.csv',
     'Required and conditional elements follow the v2.1.0 closed schema and local A2 receipt profile.'),
    ('Table 3. Validation and failure-injection evidence', 'Table_3_validation_failure_matrix.csv',
     'Counts are executed schema, canonicalisation, mutation and property evidence. Generated and bounded checks are finite and are not formal proof.'),
    ('Table 4. Executed local reference passage', 'Table_4_local_reference_execution_summary.csv',
     'Timing values are single-host descriptive measurements; they are not comparative benchmarks or production capacity estimates.'),
]


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        return rows, list(rows[0].keys()) if rows else []


def esc(value: object) -> str:
    return str(value).replace('|', '\\|').replace('\n', ' ')


def display_name(field: str) -> str:
    labels = {
        'curation_stage': 'Curation stage',
        'biomedical_accountability_question': 'Biomedical accountability question',
        'retained_evidence': 'Retained evidence',
        'excluded_content': 'Excluded content',
        'failure_control': 'Failure control',
        'component': 'Component',
        'cardinality': 'Cardinality',
        'principal fields': 'Principal fields',
        'validation_or_binding': 'Validation or binding',
        'evidence_layer': 'Evidence layer',
        'executed_units': 'Executed units',
        'expected_decision': 'Expected decision',
        'observed_result': 'Observed result',
        'interpretation_boundary': 'Interpretation boundary',
        'metric_or_descriptor': 'Metric or descriptor',
        'value': 'Value',
        'unit': 'Unit',
        'evidence_status': 'Evidence status',
        'allowable_interpretation': 'Allowable interpretation',
        'descriptor': 'Descriptor',
        'leaves': 'Leaves',
        'events': 'Events',
        'append_p50_ms': 'Append p50 (ms)',
        'append_p95_ms': 'Append p95 (ms)',
        'verify_p50_ms': 'Verify p50 (ms)',
        'verify_p95_ms': 'Verify p95 (ms)',
        'receipt_median_bytes': 'Receipt median (bytes)',
        'proof_median_bytes': 'Proof median (bytes)',
        'receipt_checks': 'Receipt checks',
        'mutation_rejections': 'Mutation rejections',
        'validation_failures': 'Validation failures',
    }
    return labels.get(field, field.replace('_', ' ').capitalize())


def render_value(field: str, value: object) -> str:
    text = str(value)
    if field in {'executed_units', 'value', 'leaves', 'events', 'receipt_median_bytes', 'proof_median_bytes', 'receipt_checks', 'validation_failures'} and text.isdigit():
        return f'{int(text):,}'
    return text


def markdown_table(rows, fields):
    headers = [display_name(f) for f in fields]
    out = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(fields)) + ' |']
    for row in rows:
        out.append('| ' + ' | '.join(esc(render_value(f, row.get(f, ''))) for f in fields) + ' |')
    return '\n'.join(out)


def main():
    parts = ['# Tables for the CMPB manuscript', '',
             'These tables are generated from retained CSV sources. Wording is deliberately bounded to the executed evidence.', '']
    for title, filename, note in TABLES:
        rows, fields = read_csv(SOURCE / filename)
        parts.extend([f'## {title}', '', markdown_table(rows, fields), '', f'**Table note.** {note}', ''])
    (OUTPUT / 'TABLES_FOR_MANUSCRIPT.md').write_text('\n'.join(parts).rstrip() + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
