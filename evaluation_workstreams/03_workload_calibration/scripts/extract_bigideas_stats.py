
from __future__ import annotations
import argparse, csv
from datetime import datetime
from pathlib import Path

FORMATS = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%m/%d/%Y %H:%M', '%Y-%m-%d %H:%M']

def parse_ts(value: str):
    for fmt in FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None

def percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return float('nan')
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values)-1) * p
    lo = int(pos); hi = min(lo+1, len(sorted_values)-1); frac = pos-lo
    return sorted_values[lo] * (1-frac) + sorted_values[hi] * frac

def main() -> None:
    parser = argparse.ArgumentParser(description='Extract timestamp interval statistics from BIG IDEAs-style CSV files.')
    parser.add_argument('--input', default='sample_data/bigideas')
    parser.add_argument('--output', default='smoke_outputs/bigideas_stats_sample.csv')
    args = parser.parse_args()
    intervals: list[float] = []; records = 0; files = 0
    for path in Path(args.input).rglob('*.csv'):
        text = path.read_text(encoding='utf-8', errors='replace').splitlines()
        if not text:
            continue
        reader = csv.DictReader(text)
        times = []
        for row in reader:
            raw = row.get('Timestamp') or row.get('timestamp') or row.get('Time') or row.get('time') or row.get('datetime')
            if raw:
                parsed = parse_ts(raw)
                if parsed:
                    times.append(parsed)
        if times:
            files += 1
        times = sorted(times)
        records += len(times)
        intervals.extend((b-a).total_seconds()/60 for a, b in zip(times, times[1:]) if (b-a).total_seconds() > 0)
    intervals = sorted(intervals)
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        fieldnames = ['metric', 'value', 'unit', 'method', 'notes']
        w = csv.DictWriter(f, fieldnames=fieldnames); w.writeheader()
        w.writerow({'metric': 'files_with_timestamps', 'value': files, 'unit': 'files', 'method': 'extracted_from_local_bigideas_files', 'notes': ''})
        w.writerow({'metric': 'records_with_timestamps', 'value': records, 'unit': 'records', 'method': 'extracted_from_local_bigideas_files', 'notes': ''})
        if intervals:
            w.writerow({'metric': 'median_interval_minutes', 'value': f'{percentile(intervals, 0.5):.6g}', 'unit': 'minutes', 'method': 'computed_from_local_bigideas_files', 'notes': ''})
            w.writerow({'metric': 'p95_interval_minutes', 'value': f'{percentile(intervals, 0.95):.6g}', 'unit': 'minutes', 'method': 'computed_from_local_bigideas_files', 'notes': ''})
            w.writerow({'metric': 'mean_interval_minutes', 'value': f'{sum(intervals)/len(intervals):.6g}', 'unit': 'minutes', 'method': 'computed_from_local_bigideas_files', 'notes': ''})
        else:
            w.writerow({'metric': 'median_interval_minutes', 'value': '', 'unit': 'minutes', 'method': 'no_intervals_available', 'notes': 'No parsable timestamp intervals found.'})
    print(f'wrote {out}')

if __name__ == '__main__':
    main()
