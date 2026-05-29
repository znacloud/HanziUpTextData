import csv
from collections import defaultdict
import argparse

def main():
    parser = argparse.ArgumentParser(description='Check for duplicate hanzi+pinyin entries in CSV.')
    parser.add_argument('--tag', type=str, default='hanzi', help='CSV tag, e.g., hanzi')
    args = parser.parse_args()
    tag = args.tag
    csv_path = f'xdhy_core_csv/a_pinyin_v1.0_{tag}.csv'
    find_duplicates(csv_path, tag)


def find_duplicates(csv_path, tag):
    seen = defaultdict(list)
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # start=2 to account for header
            key = (row['hanzi'], row['pinyin'])
            seen[key].append(i)
    
    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    if not duplicates:
        print(f'[{tag}] No duplicates found based on hanzi and pinyin.')
    else:
        print(f'[{tag}] Duplicate entries found (hanzi, pinyin):')
        for (hanzi, pinyin), lines in duplicates.items():
            print(f"[{tag}] {hanzi}, {pinyin} -> lines: {lines}")

if __name__ == '__main__':
    main()
