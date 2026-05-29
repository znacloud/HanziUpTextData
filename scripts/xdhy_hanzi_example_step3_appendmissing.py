import csv


TAG = 'single'
# File paths
MISSING_IDS_FILE = f'others/xdhy_core_hanzi_definition_v8_{TAG}_missing_ids_in_example.txt'
EXAMPLES_FILE = 'database_csv/hanzi_examples_v7.csv'
CURRENT_EXAMPLES_FILE = f'others/xdhy_core_hanzi_example_v8_{TAG}.csv'
OUTPUT_FILE = f'others/xdhy_core_hanzi_example_v8_{TAG}_appened.csv'

# Step 1: Read missing IDs into a set
missing_ids = set()
with open(MISSING_IDS_FILE, encoding='utf-8') as f:
    for line in f:
        id_ = line.strip().replace('\r', '').replace('\n', '')
        if id_:
            missing_ids.add(id_)

# Step 2: Collect missed examples from the large examples CSV
missed_examples = []
with open(EXAMPLES_FILE, encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if row and row[0] in missing_ids:
            missed_examples.append(row)

# Step 3: Write current examples to output, then append missed examples
with open(CURRENT_EXAMPLES_FILE, encoding='utf-8') as fin, \
     open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as fout:
    reader = csv.reader(fin)
    writer = csv.writer(fout)
    # Write header
    header = next(reader)
    writer.writerow(header)
    # Write existing examples
    for row in reader:
        writer.writerow(row)
    # Append missed examples
    for row in missed_examples:
        writer.writerow(row)

print(f" {TAG} {len(missing_ids)} missing ids in example. Appended {len(missed_examples)} missed examples. Output saved to {OUTPUT_FILE}") 