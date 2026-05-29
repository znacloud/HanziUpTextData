import csv
from pathlib import Path

def load_pinyin_ids(pinyin_file):
    """Load all pinyin IDs from the pinyin CSV file."""
    pinyin_ids = set()
    with open(pinyin_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pinyin_ids.add(row['pinyin_id'])
    return pinyin_ids

def load_definition_pinyin_ids(definition_file):
    """Load all pinyin IDs from the definition CSV file."""
    definition_pinyin_ids = set()
    with open(definition_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pinyin_id = row.get('pinyin_id', '')
            if pinyin_id:
                definition_pinyin_ids.add(pinyin_id)
    return definition_pinyin_ids

def check_missing_ids(source_ids, target_ids):
    """Return IDs in source_ids that are missing from target_ids."""
    return source_ids - target_ids

def main():
    # File paths
    base_dir = Path('others')
    pinyin_file = base_dir / 'xdhy_core_hanzi_pinyin_v8_cihui.csv'
    definition_file = base_dir / 'xdhy_core_hanzi_definition_v8_cihui.csv'
    
    # Load all pinyin IDs from both files
    print("Loading pinyin IDs from pinyin file...")
    pinyin_ids = load_pinyin_ids(pinyin_file)
    print(f"Loaded {len(pinyin_ids)} pinyin IDs from {pinyin_file}")
    
    print("Loading pinyin IDs from definition file...")
    definition_pinyin_ids = load_definition_pinyin_ids(definition_file)
    print(f"Loaded {len(definition_pinyin_ids)} pinyin IDs from {definition_file}")
    
    # Check for missing IDs in both directions
    missing_in_definition = check_missing_ids(pinyin_ids, definition_pinyin_ids)
    missing_in_pinyin = check_missing_ids(definition_pinyin_ids, pinyin_ids)
    
    # Report results
    if missing_in_definition:
        print(f"\nPinyin IDs in pinyin file but missing in definition file ({len(missing_in_definition)}):")
        for pid in sorted(missing_in_definition):
            print(f"  {pid}")
    else:
        print("\nAll pinyin_ids in pinyin file exist in definition file!")
    
    if missing_in_pinyin:
        print(f"\nPinyin IDs in definition file but missing in pinyin file ({len(missing_in_pinyin)}):")
        for pid in sorted(missing_in_pinyin):
            print(f"  {pid}")
    else:
        print("\nAll pinyin_ids in definition file exist in pinyin file!")
    
    # Summary
    print(f"\nSummary:")
    print(f"Total pinyin_ids in pinyin file: {len(pinyin_ids)}")
    print(f"Total pinyin_ids in definition file: {len(definition_pinyin_ids)}")
    print(f"Missing in definition file: {len(missing_in_definition)}")
    print(f"Missing in pinyin file: {len(missing_in_pinyin)}")

if __name__ == '__main__':
    main() 