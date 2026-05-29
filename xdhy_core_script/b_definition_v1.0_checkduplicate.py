import csv
import argparse
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description='Check for duplicate definition_cn entries in a CSV.')
    parser.add_argument('--tag', type=str, default='hanzi', help='CSV tag, e.g., hanzi')
    args = parser.parse_args()
    tag = args.tag
    csv_path = f'xdhy_core_csv/b_definition_v1.0_{tag}.csv'
    find_duplicates(csv_path, tag)

def find_duplicates(csv_path, tag):
    seen = defaultdict(list)
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # start=2 to account for header
            key = row['definition_cn']
            if key.strip():
                seen[(row['pinyin_id'], key)].append(i)
    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    if not duplicates:
        print(f'[{tag}] No duplicates found in definition_cn.')
    else:
        print(f'[{tag}] {len(duplicates)} duplicate entries found in definition_cn:')
        for definition_cn, lines in duplicates.items():
            print(f"[{tag}] {definition_cn} -> lines: {lines}")

if __name__ == '__main__':
    main() 