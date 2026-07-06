from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = [
        'MEASUREMENT_PROTOCOL.md',
        'experiments/workloads/W1.json',
        'experiments/workloads/W2.json',
        'experiments/workloads/W3.json',
        'experiments/workloads/W4.json',
        'experiments/workloads/W5.json',
        'schemas/results/raw_write_measurements.csv.schema.json',
        'schemas/results/run_summary.csv.schema.json',
        'schemas/results/statistical_summary.csv.schema.json',
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    schema_count = len(list((ROOT / 'schemas/results').glob('*.schema.json')))
    if schema_count < 10:
        missing.append(f'expected at least 10 schemas, found {schema_count}')
    if missing:
        print('Protocol validation: FAIL')
        for item in missing:
            print('- ' + item)
        return 1
    print('Protocol validation: PASS')
    print('workloads=5')
    print(f'result_schemas={schema_count}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
