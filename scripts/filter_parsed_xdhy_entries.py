import csv
import json

# Step 1: Load all hanzi from the CSV into a set
hanzi_set = set()
with open('database_csv/hanzi_pinyin_v7_with_sn_updated.csv', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        hanzi_set.add(row['hanzi'])

# Step 2: Stream through the large JSON and filter
filtered_entries = []
print(f"Loading {len(hanzi_set)} hanzi from the CSV")
with open('raw_data/xdhy_entries_parsed.json', encoding='utf-8') as infile:
    # The file is a list of dicts: [{hanzi1: ...}, {hanzi2: ...}, ...]
    # We'll load in chunks if needed, but let's try loading all if memory allows
    data = json.load(infile)
    for entry in data:
        # Each entry is a dict with a single key
        key = next(iter(entry))
        if key not in hanzi_set:
            filtered_entries.append(entry)

# Step 3: Write the filtered entries to a new file
with open('raw_data/xdhy_entries_parsed_filtered.json', 'w', encoding='utf-8') as outfile:
    json.dump(filtered_entries, outfile, ensure_ascii=False, indent=2)

print(f"Filtered entries written: {len(filtered_entries)}")