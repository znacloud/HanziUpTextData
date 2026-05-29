#!/usr/bin/env python3
"""
Script to extract duplicate "hanzi, definition, example" entries from jjhy_hanzi_parsed CSV files.
This script reads all jjhy_hanzi_parsed_*.csv files and identifies duplicates based on the combination
of hanzi, definition, and example fields.
"""

import pandas as pd
import glob
import os
from pathlib import Path

def main():
    # Define file paths
    tag = 'cihui'
    input_pattern = f"others/jjhy_{tag}_parsed_[0-9]*.csv"  # Only match numbered files, not the duplicate file
    output_file = f"others/jjhy_{tag}_parsed_duplicate.csv"
    
    print("Starting duplicate extraction process...")
    print(f"Looking for files matching pattern: {input_pattern}")
    
    # Find all matching CSV files
    csv_files = glob.glob(input_pattern)
    
    if not csv_files:
        print(f"No files found matching pattern: {input_pattern}")
        return
    
    print(f"Found {len(csv_files)} files:")
    for file in csv_files:
        print(f"  - {file}")
    
    # Read and combine all CSV files
    all_data = []
    for file in csv_files:
        print(f"Reading {file}...")
        try:
            df = pd.read_csv(file)
            print(f"  - Loaded {len(df)} rows from {file}")
            all_data.append(df)
        except Exception as e:
            print(f"  - Error reading {file}: {e}")
            continue
    
    if not all_data:
        print("No data loaded from any files.")
        return
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\nCombined data: {len(combined_df)} total rows")
    
    # Create a composite key for duplicate detection
    # Combine hanzi, definition, and example into a single string
    combined_df['composite_key'] = combined_df[tag].astype(str) + '|' + \
                                   combined_df['definition'].astype(str) + '|' + \
                                   combined_df['example'].astype(str)
    
    # Find duplicates based on the composite key
    print("Finding duplicates...")
    duplicates = combined_df[combined_df.duplicated(subset=['composite_key'], keep=False)]
    
    # Sort by multiple columns to ensure consistent order
    # First sort by hanzi, then definition, then example, then rank, then pinyin
    duplicates = duplicates.sort_values([ 'rank', tag, 'pinyin',  'definition', 'example'])
    
    # Remove the composite key column before saving
    duplicates = duplicates.drop('composite_key', axis=1)
    
    print(f"Found {len(duplicates)} duplicate rows")
    
    # Save duplicates to output file
    print(f"Saving duplicates to {output_file}...")
    try:
        duplicates.to_csv(output_file, index=False)
        print(f"Successfully saved {len(duplicates)} duplicate rows to {output_file}")
        
        # Print some statistics
        unique_duplicate_groups = len(duplicates.groupby([tag, 'definition', 'example']))
        print(f"Number of unique duplicate groups: {unique_duplicate_groups}")
        
        # Show some examples of duplicates
        print("\nSample of duplicates found:")
        sample_duplicates = duplicates.head(10)
        for idx, row in sample_duplicates.iterrows():
            print(f"  {tag}: {row[tag]}, Definition: {row['definition'][:50]}..., Example: {row['example']}")
            
    except Exception as e:
        print(f"Error saving to {output_file}: {e}")

if __name__ == "__main__":
    main() 