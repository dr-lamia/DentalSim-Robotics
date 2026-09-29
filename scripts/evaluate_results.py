import argparse
import csv
from statistics import mean, median


def main():
    p = argparse.ArgumentParser()
    p.add_argument('csv_file')
    args = p.parse_args()
    with open(args.csv_file, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit('No rows found')
    vals = [float(r['mean_surface_deviation_mm']) for r in rows]
    success = [int(r['success']) for r in rows]
    print(f'n={len(rows)}')
    print(f'mean_surface_deviation_mm={mean(vals):.3f}')
    print(f'median_surface_deviation_mm={median(vals):.3f}')
    print(f'success_rate={sum(success)/len(success):.3f}')

if __name__ == '__main__':
    main()
