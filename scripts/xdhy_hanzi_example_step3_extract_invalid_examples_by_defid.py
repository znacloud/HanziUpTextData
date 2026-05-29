import csv

def main():
    TAG = 'cihui'
    invalid_examples_file = f'others/xdhy_core_hanzi_example_v9_{TAG}_invalid.csv'
    no_example_defs_file = f'others/xdhy_core_hanzi_example_v9_{TAG}_no_example_defs.csv'
    output_file = f'others/xdhy_core_hanzi_example_v9_{TAG}_invalid_for_no_example_defs.csv'

    # Read definition_ids from the no_example file
    with open(no_example_defs_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        no_example_ids = set(row['definition_id'] for row in reader if row.get('definition_id'))

    # Filter invalid examples by these ids
    with open(invalid_examples_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows_to_save = [row for row in reader if row.get('definition_id') in no_example_ids]
        fieldnames = reader.fieldnames

    # Write filtered rows to output
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_save)

    print(f"Extracted {len(rows_to_save)} rows to {output_file}")

if __name__ == '__main__':
    main() 