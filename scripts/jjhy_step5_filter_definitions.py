#!/usr/bin/env python3
"""
Script to filter out rows whose definition starts with '见"' in jjhy_cihui_parsed CSV files.

This script processes all CSV files matching the pattern "others/jjhy_cihui_parsed_[0-9]*.csv"
and separates rows where the definition column starts with '见"' into separate files with "_invalid" suffix.
The filtered data (without the problematic rows) is saved to the original filename.
"""

import os
import glob
import pandas as pd
import argparse
from pathlib import Path


TAG = "hanzi"

def filter_cihui_definitions(input_dir="others", output_dir=None, dry_run=False):
    """
    Filter out rows whose definition starts with '见"' in cihui CSV files.
    
    Args:
        input_dir (str): Directory containing the CSV files
        output_dir (str): Directory to save filtered files (if None, saves in same directory)
        dry_run (bool): If True, only show what would be filtered without making changes
    """
    
    # Find all cihui files matching the pattern
    pattern = os.path.join(input_dir, f"jjhy_{TAG}_parsed_[0-9]*_filtered.csv")
    csv_files = glob.glob(pattern)
    
    if not csv_files:
        print(f"No files found matching pattern: {pattern}")
        return
    
    print(f"Found {len(csv_files)} files to process:")
    for file in csv_files:
        print(f"  - {file}")
    
    total_filtered = 0
    
    for file_path in csv_files:
        print(f"\nProcessing: {file_path}")
        
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Check if 'definition' column exists
            if 'definition' not in df.columns:
                print(f"  Warning: No 'definition' column found in {file_path}")
                continue
            
            # Count rows that start with '见"'
            mask = df['definition'].astype(str).str.startswith('见“')
            filtered_count = mask.sum()
            
            print(f"  Total rows: {len(df)}")
            print(f"  Rows to filter out: {filtered_count}")
            
            if filtered_count > 0:
                # Show examples of rows that will be filtered
                print(f"  Examples of rows to be filtered:")
                filtered_examples = df[mask].head(3)
                for idx, row in filtered_examples.iterrows():
                    print(f"    Row {idx}: {row.get(TAG, 'N/A')} - {row.get('definition', 'N/A')}")
            
            if not dry_run:
                # Separate rows that start with '见"' and those that don't
                df_filtered = df[~mask]  # Rows that don't start with '见"'
                df_invalid = df[mask]    # Rows that start with '见"'
                
                # Determine output paths
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                dir_path = output_dir if output_dir else os.path.dirname(file_path)
                
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                
                # Save the filtered data (rows without '见"')
                filtered_output_path = os.path.join(dir_path, f"{base_name}_filtered.csv")
                df_filtered.to_csv(filtered_output_path, index=False)
                print(f"  Saved filtered file: {filtered_output_path}")
                print(f"  Remaining rows: {len(df_filtered)}")
                
                # Save the invalid rows (rows with '见"')
                if len(df_invalid) > 0:
                    invalid_output_path = os.path.join(dir_path, f"{base_name}_invalid.csv")
                    df_invalid.to_csv(invalid_output_path, index=False)
                    print(f"  Saved invalid rows to: {invalid_output_path}")
                    print(f"  Invalid rows: {len(df_invalid)}")
            else:
                print(f"  [DRY RUN] Would filter out {filtered_count} rows")
                if filtered_count > 0:
                    print(f"  [DRY RUN] Would save invalid rows to: {os.path.splitext(os.path.basename(file_path))[0]}_invalid.csv")
            
            total_filtered += filtered_count
            
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
    
    print(f"\nSummary:")
    print(f"Total rows filtered out: {total_filtered}")
    if dry_run:
        print("This was a dry run - no files were actually modified.")


def main():
    parser = argparse.ArgumentParser(
        description="Filter out rows whose definition starts with '见\"' in cihui CSV files"
    )
    parser.add_argument(
        "--input-dir", 
        default="others",
        help="Directory containing the CSV files (default: others)"
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to save filtered files (if not specified, saves in same directory as original files)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be filtered without making changes"
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist.")
        return 1
    
    # Run the filtering
    filter_cihui_definitions(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        dry_run=args.dry_run
    )
    
    return 0


if __name__ == "__main__":
    exit(main()) 