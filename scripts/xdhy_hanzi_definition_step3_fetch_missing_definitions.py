import csv

TAG = 'single'
# File paths
ids_file = f'others/xdhy_core_hanzi_definition_v8_{TAG}_missing_ids_in_example.txt'
definition_csv = f'others/xdhy_core_hanzi_definition_v8_{TAG}.csv'
output_csv = f'others/xdhy_core_hanzi_definition_v8_{TAG}_missing_ids_in_example.csv'

# Read missing IDs
with open(ids_file, 'r', encoding='utf-8') as f:
    missing_ids = set(line.strip() for line in f if line.strip())

# Fetch matching rows
with open(definition_csv, 'r', encoding='utf-8') as infile, \
     open(output_csv, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames or [])
    writer.writeheader()
    for row in reader:
        if row['definition_id'] in missing_ids:
            writer.writerow(row) 