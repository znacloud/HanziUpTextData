import pandas as pd
import os

def filter_combinations(input_file):
    """
    Filter combinations to remove items that equal the hanzi itself.
    
    Args:
        input_file: Path to the input CSV file
    """
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    print(f"Total rows: {len(df)}")
    
    # Track statistics
    rows_modified = 0
    total_items_removed = 0
    
    def filter_row_combinations(row):
        nonlocal rows_modified, total_items_removed
        
        hanzi = row['hanzi']
        combinations = row['combinations']
        
        # Handle empty or NaN combinations
        if pd.isna(combinations) or combinations == '':
            return combinations
        
        # Split by Chinese vertical bar
        items = combinations.split('｜')
        original_count = len(items)
        
        # Filter out items that equal the hanzi itself
        filtered_items = [item.strip() for item in items if item.strip() != hanzi]
        
        # Track changes
        if len(filtered_items) < original_count:
            rows_modified += 1
            total_items_removed += (original_count - len(filtered_items))
            print(f"Row {row['hanzi_id']}: '{hanzi}' - Removed {original_count - len(filtered_items)} items")
        
        # Return filtered combinations joined by Chinese vertical bar
        return '｜'.join(filtered_items) if filtered_items else ''
    
    # Apply filtering
    df['combinations'] = df.apply(filter_row_combinations, axis=1)
    
    # Save to the same directory with a new name
    output_dir = os.path.dirname(input_file)
    output_file = os.path.join(output_dir, 'jjhy_core_hanzi_combinations_filtered.csv')
    
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n=== Summary ===")
    print(f"Rows modified: {rows_modified}")
    print(f"Total items removed: {total_items_removed}")
    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    # Use relative path from root directory
    input_file = "jjhy_csv/core_csv_with_combinations/jjhy_core_hanzi_combinations.csv"
    filter_combinations(input_file)
