#!/usr/bin/env python3
"""
Script to filter hanzi data by extracting specific columns from invalid parsed files
and removing entries that exist in filtered files.

This script:
1. Extracts "rank,hanzi,pinyin,mismatch_parsed,invalid_parsed,has_subdefs" from 
   "others/jjhy_hanzi_invalid_parsed_*.csv" files
2. Extracts "rank,hanzi" from "jjhy_csv/final_merged/jjhy_hanzi_parsed_*_filtered.csv" files  
3. Filters out entries from step 1 that have matching (rank,hanzi) pairs in step 2
"""

import pandas as pd
import glob
import os
import re

TAG = "cihui"

def find_matching_files():
    """Find all matching CSV files based on the specified patterns."""
    # Find invalid parsed files
    invalid_files = glob.glob(f"others/jjhy_{TAG}_invalid_parsed_*.csv")
    
    # Find filtered files
    filtered_files = glob.glob(f"jjhy_csv/final_merged/jjhy_{TAG}_parsed_*_filtered.csv")
    
    print(f"Found {len(invalid_files)} invalid parsed files:")
    for f in invalid_files:
        print(f"  - {f}")
    
    print(f"\nFound {len(filtered_files)} filtered files:")
    for f in filtered_files:
        print(f"  - {f}")
    
    return invalid_files, filtered_files

def extract_number_from_filename(filename):
    """Extract the number from filename like 'jjhy_hanzi_invalid_parsed_3500.csv'."""
    match = re.search(r'_(\d+)(?:_filtered)?\.csv$', filename)
    return int(match.group(1)) if match else None

def process_files():
    """Main processing function."""
    invalid_files, filtered_files = find_matching_files()
    
    if not invalid_files:
        print("No invalid parsed files found!")
        return
    
    if not filtered_files:
        print("No filtered files found!")
        return
    
    # Create a mapping of numbers to filtered files for easy lookup
    filtered_file_map = {}
    for f in filtered_files:
        num = extract_number_from_filename(f)
        if num:
            filtered_file_map[num] = f
    
    # Process each invalid file
    for invalid_file in invalid_files:
        num = extract_number_from_filename(invalid_file)
        if num is None:
            print(f"Warning: Could not extract number from {invalid_file}")
            continue
            
        print(f"\nProcessing files for number {num}...")
        
        # Step 1: Extract specified columns from invalid file
        try:
            print(f"Reading invalid file: {invalid_file}")
            invalid_df = pd.read_csv(invalid_file)
            
            # Check if all required columns exist
            required_cols = ['rank', TAG, 'pinyin', 'mismatch_parsed', 'invalid_parsed', 'has_subdefs', 'raw_html']
            missing_cols = [col for col in required_cols if col not in invalid_df.columns]
            
            if missing_cols:
                print(f"Warning: Missing columns in {invalid_file}: {missing_cols}")
                print(f"Available columns: {list(invalid_df.columns)}")
                continue
            
            # Extract required columns
            step1_data = invalid_df[required_cols].copy()
            print(f"Extracted {len(step1_data)} rows from invalid file")
            
        except Exception as e:
            print(f"Error reading {invalid_file}: {e}")
            continue
        
        # Step 2: Extract rank,hanzi from corresponding filtered file
        if num not in filtered_file_map:
            print(f"Warning: No corresponding filtered file found for number {num}")
            # If no corresponding filtered file, output all data from step 1
            output_file = f"jjhy_csv/missed_{TAG}_html_{num}.csv"
            step1_data.to_csv(output_file, index=False)
            print(f"No filtering applied. Saved {len(step1_data)} rows to {output_file}")
            continue
        
        filtered_file = filtered_file_map[num]
        
        try:
            print(f"Reading filtered file: {filtered_file}")
            filtered_df = pd.read_csv(filtered_file)
            
            # Check if required columns exist
            if 'rank' not in filtered_df.columns or TAG not in filtered_df.columns:
                print(f"Warning: Missing rank or hanzi columns in {filtered_file}")
                print(f"Available columns: {list(filtered_df.columns)}")
                continue
            
            # Extract rank,hanzi pairs
            step2_data = filtered_df[['rank', TAG]].copy()
            print(f"Extracted {len(step2_data)} (rank,hanzi) pairs from filtered file")
            
        except Exception as e:
            print(f"Error reading {filtered_file}: {e}")
            continue
        
        # Step 3: Filter out step2 data from step1 data
        # Create a set of (rank, hanzi) tuples from step2 for efficient lookup
        filtered_pairs = set(zip(step2_data['rank'], step2_data[TAG]))
        print(f"Created filter set with {len(filtered_pairs)} unique (rank,hanzi) pairs")
        
        # Filter step1 data by removing rows that match any (rank,hanzi) pair in step2
        initial_count = len(step1_data)
        mask = ~step1_data.apply(lambda row: (row['rank'], row[TAG]) in filtered_pairs, axis=1)
        filtered_result = step1_data[mask].copy()
        
        removed_count = initial_count - len(filtered_result)
        print(f"Filtered out {removed_count} rows, {len(filtered_result)} rows remaining")
        
        # Save result
        output_file = f"jjhy_csv/missed_{TAG}_html_{num}.csv"
        filtered_result.to_csv(output_file, index=False)
        print(f"Saved filtered result to {output_file}")
        
        # Print some statistics
        print(f"Summary for {num}:")
        print(f"  - Initial invalid entries: {initial_count}")
        print(f"  - Filtered entries to remove: {len(filtered_pairs)}")
        print(f"  - Entries removed: {removed_count}")
        print(f"  - Final result entries: {len(filtered_result)}")

def main():
    """Main function."""
    print("Hanzi Data Filter Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("others") or not os.path.exists("jjhy_csv/final_merged"):
        print("Error: Please run this script from the project root directory.")
        print("Expected directories 'others' and 'jjhy_csv/final_merged' not found.")
        return
    
    process_files()
    print("\nScript completed!")

if __name__ == "__main__":
    main()
