import csv
import os

TAG = 'cihui'
# File paths
PINYIN_FILE = f'xdhy_core_csv/a_pinyin_v1.1_{TAG}.csv'
MISSING_FILE = f'xdhy_core_csv/b_definition_v1.1_{TAG}_missing_ids_in_example.csv'
OUTPUT_FILE = f'xdhy_core_csv/b_definition_v1.1_{TAG}_missing_ids_in_example_with_hanzipinyin.csv'

def load_pinyin_map(pinyin_file):
    """Load pinyin_id -> (hanzi, pinyin) mapping from the pinyin file."""
    mapping = {}
    with open(pinyin_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row['pinyin_id']] = (row['hanzi'], row['pinyin'])
    return mapping

def prepend_hanzi_pinyin(pinyin_map, missing_file, output_file):
    with open(missing_file, encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8', newline='') as fout:
        reader = csv.DictReader(fin)
        fieldnames = ['hanzi', 'pinyin'] + list(reader.fieldnames or [])
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            pinyin_id = row['pinyin_id']
            hanzi, pinyin = pinyin_map.get(pinyin_id, ('', ''))
            new_row = {'hanzi': hanzi, 'pinyin': pinyin}
            new_row.update(row)
            writer.writerow(new_row)

def main():
    pinyin_map = load_pinyin_map(PINYIN_FILE)
    prepend_hanzi_pinyin(pinyin_map, MISSING_FILE, OUTPUT_FILE)
    print(f"Output written to {OUTPUT_FILE}")

if __name__ == '__main__':
    main() 