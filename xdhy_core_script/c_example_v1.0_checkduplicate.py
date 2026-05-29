import csv
import argparse
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description='Check for duplicate example_cn entries in a CSV.')
    parser.add_argument('--tag', type=str, default='hanzi', help='CSV tag, e.g., hanzi')
    args = parser.parse_args()
    tag = args.tag
    csv_path = f'xdhy_core_csv/c_example_v1.0_{tag}.csv'
    find_duplicates(csv_path, tag)

def find_duplicates(csv_path, tag):
    seen = defaultdict(list)
    example_rows = []
    example_header = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        example_header = reader.fieldnames or []
        for row in reader:
            key = row['example_cn']
            if key.strip():
                seen[key].append((row['definition_id'], row['example_sn']))
                example_rows.append(row)
    duplicates = {k: get_duplicate_numbers(v) for k, v in seen.items() if len(v) > 1 and has_any_neighbors(getDefIDFromIdSnPairList(v))}
    if not duplicates:
        print(f'[{tag}] No duplicates found in example_cn.')
        return
    print(f'[{tag}] {len(duplicates)} duplicate entries found in example_cn:')
    for example_cn, lines in duplicates.items():
        print(f"[{tag}] {example_cn} -> definition_ids: {lines}")
    print(f'[{tag}] Total duplicate entries: {len(duplicates)}')

    # Load definition file into a dict: definition_id -> row
    def_path = f'xdhy_core_csv/b_definition_v1.0_{tag}.csv'
    def_dict = {}
    with open(def_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            def_dict[row['definition_id']] = row

    # Load pinyin file into a dict: pinyin_id -> row
    pinyin_path = f'xdhy_core_csv/a_pinyin_v1.0_{tag}.csv'
    pinyin_dict = {}
    with open(pinyin_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pinyin_dict[row['pinyin_id']] = row

    # Prepare output rows
    duplicate_def_id_sn_pairs = []
    for example_cn, lines in duplicates.items():
        duplicate_def_id_sn_pairs.extend(lines)
    duplicate_def_id_sn_pairs = list(set(duplicate_def_id_sn_pairs))
    print(f'[{tag}] {len(duplicate_def_id_sn_pairs)} unique duplicate definition_ids')

    output_rows = []
    filtred_example_rows = []
    header = ['pinyin_id', 'hanzi', 'pinyin', 'definition_id', 'definition_sn', 'definition_cn', 'example_sn', 'example_cn']
    for row in example_rows:
        definition_id = row['definition_id']
        example_sn = row['example_sn']
        if (definition_id, example_sn) in duplicate_def_id_sn_pairs:
            definition_id = row['definition_id']
            example_sn = row['example_sn']
            example_cn = row['example_cn']
            def_row = def_dict.get(definition_id, {})
            pinyin_id = def_row.get('pinyin_id', '')
            definition_sn = def_row.get('definition_sn', '')
            definition_cn = def_row.get('definition_cn', '')
            pinyin_row = pinyin_dict.get(pinyin_id, {})
            hanzi = pinyin_row.get('hanzi', '')
            pinyin = pinyin_row.get('pinyin', '')
            output_rows.append({
                'pinyin_id': pinyin_id,
                'hanzi': hanzi,
                'pinyin': pinyin,
                'definition_id': definition_id,
                'definition_sn': definition_sn,
                'definition_cn': definition_cn,
                'example_sn': example_sn,
                'example_cn': example_cn
            })
        else:
            filtred_example_rows.append(row)

    # sort output_rows by example_cn then by definition_id
    output_rows.sort(key=lambda x: (x['example_cn'], x['definition_id']))
    # Write to output CSV
    output_path = f'xdhy_core_csv/c_example_v1.0_duplicate_{tag}.csv'
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)
    print(f'[{tag}] Output written to {output_path}')

    # Write to filtred example CSV
    filtred_example_path = f'xdhy_core_csv/c_example_v1.1_{tag}.csv'
    with open(filtred_example_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=example_header)
        writer.writeheader()
        for row in filtred_example_rows:
            writer.writerow(row)
    print(f'[{tag}] Filtred example output written to {filtred_example_path}')

def isDefIDClose(def_ids):
    first = int(def_ids[0])
    for def_id in def_ids[1:]:
        if abs(int(def_id) - first) < 10:
            return True
    return False

def getDefIDFromIdSnPairList(id_sn_pair_list):
    def_ids = [x[0] for x in id_sn_pair_list]
    return def_ids

def has_any_neighbors(nums_strs, delta=1):
    nums = [int(x) for x in nums_strs]
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(nums[i] - nums[j]) <= delta:
                return True
    return False

def find_disnormal_numbers(nums_strs, delta=1):
    nums = [int(x) for x in nums_strs]
    nums_sorted = sorted(nums)
    if len(nums) < 3:
        return [], nums_sorted

    n = len(nums)
    # Use sliding window to find the largest group of consecutive neighbors
    max_group = []
    left = 0
    for right in range(n):
        # Move left pointer to maintain all numbers in window within delta of each other
        while nums_sorted[right] - nums_sorted[left] > delta * (right - left):
            left += 1
        if right - left + 1 > len(max_group):
            max_group = nums_sorted[left:right+1]
    normal_set = set(max_group)
    disnormal = [x for x in nums if x not in normal_set]
    return sorted(disnormal), sorted(normal_set)

def get_duplicate_numbers(id_sn_pair_list):
    _, normal_set = find_disnormal_numbers(getDefIDFromIdSnPairList(id_sn_pair_list))
    duplicate_def_ids = [str(x) for x in normal_set[:-1]]
    return [(x, y) for x, y in id_sn_pair_list if x in duplicate_def_ids]

if __name__ == '__main__':
    main()
    # nums = ['521111', '521112', '521113']
    # print(has_any_neighbors(nums))
    # disnormal, normal_set = find_disnormal_numbers(nums)
    # print(f'disnormal: {disnormal}')
    # print(f'normal_set: {normal_set}')
    # print(f'duplicate_numbers: {get_duplicate_numbers(nums)}')