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

def check_definition_pinyin_ids(definition_file, pinyin_ids):
    """Check if all pinyin IDs in definition file exist in pinyin_ids set."""
    missing_pinyin_ids = set()
    missing_ref_pinyin_ids = set()
    
    with open(definition_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # start=2 because of header row
            pinyin_id = row.get('pinyin_id', '')
            ref_pinyin_id = row.get('ref_pinyin_id', '')
            
            if pinyin_id and pinyin_id not in pinyin_ids:
                missing_pinyin_ids.add((pinyin_id, row_num))
            
            if ref_pinyin_id and ref_pinyin_id not in pinyin_ids:
                missing_ref_pinyin_ids.add((ref_pinyin_id, row_num))
    
    return missing_pinyin_ids, missing_ref_pinyin_ids

def check_pinyin_file_pinyin_ids(pinyin_file, definition_pinyin_ids):
    """Check if all pinyin IDs in pinyin file exist in definition_pinyin_ids set."""
    missing_in_definition = set()
    
    with open(pinyin_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # start=2 because of header row
            pinyin_id = row.get('pinyin_id', '')
            
            if pinyin_id and pinyin_id not in definition_pinyin_ids:
                missing_in_definition.add((pinyin_id, row_num))
    
    return missing_in_definition

def load_definition_pinyin_ids(definition_file):
    """Load all pinyin IDs and ref_pinyin_ids from the definition CSV file."""
    definition_pinyin_ids = set()
    
    with open(definition_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pinyin_id = row.get('pinyin_id', '')
            ref_pinyin_id = row.get('ref_pinyin_id', '')
            
            if pinyin_id:
                definition_pinyin_ids.add(pinyin_id)
            if ref_pinyin_id:
                definition_pinyin_ids.add(ref_pinyin_id)
    
    return definition_pinyin_ids

def main():
    # File paths
    base_dir = Path('database_csv')
    pinyin_file = base_dir / 'hanzi_pinyin_v7_with_sn_updated.csv'
    definition_file = base_dir / 'hanzi_definition_v7_with_pos_updated.csv'
    
    # Load all pinyin IDs from pinyin file
    print("Loading pinyin IDs from pinyin file...")
    pinyin_ids = load_pinyin_ids(pinyin_file)
    print(f"Loaded {len(pinyin_ids)} pinyin IDs from {pinyin_file}")
    
    # Load all pinyin IDs from definition file
    print("Loading pinyin IDs from definition file...")
    definition_pinyin_ids = load_definition_pinyin_ids(definition_file)
    print(f"Loaded {len(definition_pinyin_ids)} pinyin IDs from {definition_file}")
    
    # Check definition file against pinyin file
    print("\nChecking definition file against pinyin file...")
    missing_pinyin_ids, missing_ref_pinyin_ids = check_definition_pinyin_ids(definition_file, pinyin_ids)
    
    # Check pinyin file against definition file
    print("\nChecking pinyin file against definition file...")
    missing_in_definition = check_pinyin_file_pinyin_ids(pinyin_file, definition_pinyin_ids)
    
    # Report results for definition file check
    if missing_pinyin_ids:
        print("\nMissing pinyin_ids in definition file (not found in pinyin file):")
        for pinyin_id, line_num in sorted(missing_pinyin_ids):
            print(f"Line {line_num}: pinyin_id '{pinyin_id}' not found in pinyin file")
    else:
        print("\nAll pinyin_ids in definition file exist in pinyin file!")
    
    if missing_ref_pinyin_ids:
        print("\nMissing ref_pinyin_ids in definition file (not found in pinyin file):")
        for ref_pinyin_id, line_num in sorted(missing_ref_pinyin_ids):
            print(f"Line {line_num}: ref_pinyin_id '{ref_pinyin_id}' not found in pinyin file")
    else:
        print("\nAll ref_pinyin_ids in definition file exist in pinyin file!")
    
    # Report results for pinyin file check
    if missing_in_definition:
        print("\nMissing pinyin_ids in pinyin file (not found in definition file):")
        for pinyin_id, line_num in sorted(missing_in_definition):
            print(f"Line {line_num}: pinyin_id '{pinyin_id}' not found in definition file")
    else:
        print("\nAll pinyin_ids in pinyin file exist in definition file!")
    
    # Summary
    print(f"\nSummary:")
    print(f"Total missing pinyin_ids in definition file: {len(missing_pinyin_ids)}")
    print(f"Total missing ref_pinyin_ids in definition file: {len(missing_ref_pinyin_ids)}")
    print(f"Total missing pinyin_ids in pinyin file: {len(missing_in_definition)}")

if __name__ == '__main__':
    main() 