
from __future__ import annotations
import argparse, csv, gzip, json
from collections import Counter
from pathlib import Path

def open_text(path: Path):
    if path.suffix == '.gz':
        return gzip.open(path, 'rt', encoding='utf-8', errors='replace')
    return path.open('r', encoding='utf-8', errors='replace')

def main() -> None:
    parser = argparse.ArgumentParser(description='Extract simple resource counts from MIMIC-on-FHIR NDJSON/JSON files.')
    parser.add_argument('--input', default='sample_data/mimic_fhir')
    parser.add_argument('--output', default='smoke_outputs/mimic_fhir_stats_sample.csv')
    args = parser.parse_args()
    counts: Counter[str] = Counter(); files = 0; sizes: list[int] = []
    for path in Path(args.input).rglob('*'):
        if not (path.name.endswith('.ndjson') or path.name.endswith('.json') or path.name.endswith('.ndjson.gz') or path.name.endswith('.json.gz')):
            continue
        files += 1
        with open_text(path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                counts[obj.get('resourceType', 'UNKNOWN')] += 1
                sizes.append(len(line.encode('utf-8')))
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        fieldnames = ['metric', 'value', 'unit', 'method', 'notes']
        w = csv.DictWriter(f, fieldnames=fieldnames); w.writeheader()
        w.writerow({'metric': 'files_read', 'value': files, 'unit': 'files', 'method': 'extracted_from_local_mimic_fhir_files', 'notes': ''})
        for key, value in sorted(counts.items()):
            w.writerow({'metric': f'resource_count_{key}', 'value': value, 'unit': 'resources', 'method': 'extracted_from_local_mimic_fhir_files', 'notes': ''})
        w.writerow({'metric': 'total_resources', 'value': sum(counts.values()), 'unit': 'resources', 'method': 'extracted_from_local_mimic_fhir_files', 'notes': ''})
        mean_line = (sum(sizes) / len(sizes)) if sizes else 0
        w.writerow({'metric': 'mean_line_bytes', 'value': f'{mean_line:.3f}', 'unit': 'bytes', 'method': 'computed_from_local_mimic_fhir_files', 'notes': ''})
    print(f'wrote {out}')

if __name__ == '__main__':
    main()
