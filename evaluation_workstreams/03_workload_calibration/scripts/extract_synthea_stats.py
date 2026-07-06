
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path

def iter_json_files(root: Path):
    for p in root.rglob('*.json'):
        yield p, json.loads(p.read_text(encoding='utf-8'))
    for p in root.rglob('*.ndjson'):
        for line in p.read_text(encoding='utf-8').splitlines():
            if line.strip():
                yield p, json.loads(line)

def main() -> None:
    parser = argparse.ArgumentParser(description='Extract simple resource counts from Synthea FHIR JSON/NDJSON output.')
    parser.add_argument('--input', default='sample_data/synthea_fhir')
    parser.add_argument('--output', default='smoke_outputs/synthea_stats_sample.csv')
    args = parser.parse_args()
    counts: Counter[str] = Counter(); sizes: list[int] = []
    for _p, obj in iter_json_files(Path(args.input)):
        if obj.get('resourceType') == 'Bundle':
            for entry in obj.get('entry', []):
                res = entry.get('resource', {})
                counts[res.get('resourceType', 'UNKNOWN')] += 1
                sizes.append(len(json.dumps(res, sort_keys=True, separators=(',', ':'))))
        else:
            counts[obj.get('resourceType', 'UNKNOWN')] += 1
            sizes.append(len(json.dumps(obj, sort_keys=True, separators=(',', ':'))))
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        fieldnames = ['metric', 'value', 'unit', 'method', 'notes']
        w = csv.DictWriter(f, fieldnames=fieldnames); w.writeheader()
        for key, value in sorted(counts.items()):
            w.writerow({'metric': f'resource_count_{key}', 'value': value, 'unit': 'resources', 'method': 'extracted_from_local_synthea_output', 'notes': ''})
        w.writerow({'metric': 'total_resources', 'value': sum(counts.values()), 'unit': 'resources', 'method': 'extracted_from_local_synthea_output', 'notes': ''})
        mean_size = (sum(sizes) / len(sizes)) if sizes else 0
        w.writerow({'metric': 'mean_resource_size_bytes', 'value': f'{mean_size:.3f}', 'unit': 'bytes', 'method': 'computed_from_local_synthea_output', 'notes': ''})
    print(f'wrote {out}')

if __name__ == '__main__':
    main()
