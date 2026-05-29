import pandas as pd
import os

def extract_unique_hanzi():
    """
    Extract unique hanzi_id and hanzi column values from jjhy_core_hanzi_pinyin.csv
    and save to jjhy_core_hanzi.csv
    """
    # Define file paths
    input_file = "database_csv/jjhy_core_hanzi_pinyin.csv"
    output_file = "jjhy_csv/core_csv_latest/jjhy_core_hanzi.csv"
    
    # Read the input CSV file
    print(f"Reading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # Display initial data info
    print(f"Total rows in input file: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Extract unique hanzi_id and hanzi columns
    print("\nExtracting unique hanzi_id and hanzi values...")
    unique_hanzi = df[['hanzi_id', 'hanzi']].drop_duplicates()
    
    # Sort by hanzi_id
    unique_hanzi = unique_hanzi.sort_values('hanzi_id').reset_index(drop=True)
    
    print(f"Unique hanzi entries: {len(unique_hanzi)}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        print(f"\nCreating directory: {output_dir}")
        os.makedirs(output_dir)
    
    # Save to output file
    print(f"\nSaving results to {output_file}...")
    unique_hanzi.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n✓ Successfully saved {len(unique_hanzi)} unique hanzi entries to {output_file}")
    
    # Display first few rows as preview
    print("\nPreview of output data:")
    print(unique_hanzi.head(10))

if __name__ == "__main__":
    extract_unique_hanzi()
