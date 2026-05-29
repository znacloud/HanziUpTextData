import csv
from pathlib import Path

def load_definition_ids(definition_file):
    """Load all definition IDs from the definition CSV file."""
    definition_ids = set()
    with open(definition_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            definition_id = row.get('definition_id', '')
            if definition_id:
                definition_ids.add(definition_id)
    return definition_ids

def load_example_definition_ids(example_file):
    """Load all definition IDs from the example CSV file."""
    example_definition_ids = set()
    with open(example_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            definition_id = row.get('definition_id', '')
            if definition_id:
                example_definition_ids.add(definition_id)
    return example_definition_ids

def check_missing_ids(source_ids, target_ids):
    """Return IDs in source_ids that are missing from target_ids."""
    return source_ids - target_ids

def main():
    TAG = 'cihui'
    # File paths
    definition_file = Path(f'others/xdhy_core_hanzi_definition_v8_{TAG}.csv')
    example_file = Path(f'others/xdhy_core_hanzi_example_v8_{TAG}_appened.csv')
    
    # Load all definition IDs from both files
    print("Loading definition IDs from definition file...")
    definition_ids = load_definition_ids(definition_file)
    print(f"Loaded {len(definition_ids)} definition IDs from {definition_file}")
    
    print("Loading definition IDs from example file...")
    example_definition_ids = load_example_definition_ids(example_file)
    print(f"Loaded {len(example_definition_ids)} definition IDs from {example_file}")
    
    # Check for missing IDs in both directions
    missing_in_example = check_missing_ids(definition_ids, example_definition_ids)
    missing_in_definition = check_missing_ids(example_definition_ids, definition_ids)
    
    # Report results
    if missing_in_example:
        print(f"\nDefinition IDs in definition file but missing in example file ({len(missing_in_example)}):")
        for did in sorted(missing_in_example):
            print(f"  {did}",end=',')
        # Save the missing ids to a file
        with open(f'others/xdhy_core_hanzi_definition_v8_{TAG}_missing_ids_in_example.txt', 'w', encoding='utf-8') as f:
            for did in sorted(missing_in_example):
                f.write(f"{did}\n")
    else:
        print("\nAll definition_ids in definition file exist in example file!")
    
    if missing_in_definition:
        print(f"\nDefinition IDs in example file but missing in definition file ({len(missing_in_definition)}):")
        for did in sorted(missing_in_definition):
            print(f"  {did}",end=',')
        # Save the missing ids to a file
        with open(f'others/xdhy_core_hanzi_example_v8_{TAG}_missing_ids_in_definition.txt', 'w', encoding='utf-8') as f:
            for did in sorted(missing_in_definition):
                f.write(f"{did}\n")
    else:
        print("\nAll definition_ids in example file exist in definition file!")
    
    # Summary
    print(f"\nSummary:")
    print(f"Total definition_ids in definition file: {len(definition_ids)}")
    print(f"Total definition_ids in example file: {len(example_definition_ids)}")
    print(f"Missing in example file: {len(missing_in_example)}")
    print(f"Missing in definition file: {len(missing_in_definition)}")

if __name__ == '__main__':
    main() 