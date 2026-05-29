import glob
import csv
import os

# Define the pattern and output file
input_pattern = os.path.join('others', 'hanzi_definitions_better_selection_DS_batch_*.csv')
output_file = os.path.join('others', 'hanzi_definitions_better_selection_DS.csv')

# Get all matching files and sort them for consistency
input_files = sorted(glob.glob(input_pattern))

if not input_files:
    print('No files found to merge.')
    exit(1)

with open(output_file, 'w', newline='', encoding='utf-8') as fout:
    writer = None
    for idx, file in enumerate(input_files):
        with open(file, 'r', encoding='utf-8') as fin:
            reader = csv.reader(fin)
            header = next(reader)
            if writer is None:
                writer = csv.writer(fout)
                writer.writerow(header)  # Write header only once
            for row in reader:
                writer.writerow(row)

print(f'Merged {len(input_files)} files into {output_file}') 