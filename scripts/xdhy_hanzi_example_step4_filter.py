import csv
import re

TAG = 'cihui'
definition_file = f'others/xdhy_core_hanzi_definition_v8_{TAG}.csv'
input_file = f'others/xdhy_core_hanzi_example_v8_{TAG}_appened.csv'
output_file = f'others/xdhy_core_hanzi_example_v9_{TAG}_filtered.csv'
invalid_examples_file = f'others/xdhy_core_hanzi_example_v9_{TAG}_invalid.csv'

def has_alphabet_chars(text):
    return bool(re.search(r'[a-zA-Z]', text))

def is_real_example(def_id, example_cn, example_en, man_valid_examples_ids):
    isValid = ('[' not in example_en and ']' not in example_en and 
            '[' not in example_cn and ']' not in example_cn and
            not has_alphabet_chars(example_cn))
    # if not isValid:
    #     isValid = def_id in man_valid_examples_ids
    return isValid

def main():
    examples_by_def = {}
    total_examples = 0
    invalid_examples = []
    man_valid_examples_ids = set()

    with open(input_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            def_id = row['definition_id']
            examples_by_def.setdefault(def_id, []).append(row)
            total_examples += 1

    ids_missing_examples = []
    filtered_rows = []
    filtered_count = 0
    for def_id, examples in examples_by_def.items():
        # Filter to real examples
        real_examples = [ex for ex in examples if is_real_example(def_id, ex['example_cn'], ex['example_en'], man_valid_examples_ids)]
        # Collect invalid examples
        invalid_examples.extend([ex for ex in examples if not is_real_example(def_id, ex['example_cn'], ex['example_en'], man_valid_examples_ids)])
        if real_examples:
            if TAG == 'single':
                # Pick all
                filtered_rows.extend(real_examples)
                filtered_count += len(real_examples)
            else:
                # Pick the one with the longest example_cn
                best = max(real_examples, key=lambda ex: len(ex['example_cn']))
                filtered_rows.append(best)
                filtered_count += 1
        else:
            # All are not real, save the id
            ids_missing_examples.append(def_id)

    # Write output
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['definition_id', 'example_sn', 'example_cn', 'example_en', 'example_img'])
        writer.writeheader()
        writer.writerows(filtered_rows)

    # Write invalid examples
    if invalid_examples:
        with open(invalid_examples_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['definition_id', 'example_sn', 'example_cn', 'example_en', 'example_img'])
            writer.writeheader()
            writer.writerows(invalid_examples)

    # For ids in ids_missing_examples, save the definition rows to a new file named "xdhy_core_hanzi_definition_v9_{TAG}_no_example.csv"
    with open(f'others/xdhy_core_hanzi_definition_v9_{TAG}_no_example.csv', 'w', encoding='utf-8', newline='') as outfile:
        with open(definition_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            missing_count = 0
            for row in reader:
                if not row or not row.get('definition_id'):
                    continue
                if row['definition_id'] in ids_missing_examples:
                    writer.writerow(row)
                    missing_count += 1

    # Print statistics
    print(f"Total examples processed: {total_examples}")
    print(f"Filtered (valid) examples: {filtered_count}")
    print(f"Invalid examples filtered out: {len(invalid_examples)}")
    print(f"Definitions missing valid examples: {len(ids_missing_examples)}")
    print(f"Definition rows written to no_example file: {missing_count}")

if __name__ == '__main__':
    main() 