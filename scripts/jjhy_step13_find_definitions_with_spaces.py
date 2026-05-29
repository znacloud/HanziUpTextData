#!/usr/bin/env python3
"""
Script to find rows with spaces in the definition column from CSV files
and save them to a new directory for fixing.
Excludes rows that have non-empty examples.
"""

import os
import csv
import pandas as pd
from pathlib import Path

def find_definitions_with_spaces(input_dir, output_dir):
    """
    Process all CSV files in input_dir, find rows with spaces in definition column,
    exclude rows with non-empty examples, and save them to output_dir with the same filename.
    
    Args:
        input_dir (str): Path to input directory containing CSV files
        output_dir (str): Path to output directory for saving filtered rows
    """
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get all CSV files in the input directory
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    print(f"Found {len(csv_files)} CSV files to process")
    
    total_rows_processed = 0
    total_rows_with_spaces = 0
    total_rows_excluded = 0
    
    for csv_file in csv_files:
        input_path = os.path.join(input_dir, csv_file)
        output_path = os.path.join(output_dir, csv_file)
        
        print(f"\nProcessing: {csv_file}")
        
        try:
            # Read the CSV file
            df = pd.read_csv(input_path)
            
            # Check if required columns exist
            if 'definition' not in df.columns:
                print(f"  Warning: 'definition' column not found in {csv_file}")
                continue
            
            if 'example' not in df.columns:
                print(f"  Warning: 'example' column not found in {csv_file}")
                continue
            
            # Find rows where definition contains at least one space
            # Convert to string and check for spaces
            rows_with_spaces = df[df['definition'].astype(str).str.contains(r'\s', na=False)]
            
            # Exclude rows that have non-empty examples
            # Check if example column has non-empty values (not NaN, not empty string)
            rows_with_spaces_no_examples = rows_with_spaces[
                (rows_with_spaces['example'].isna()) | 
                (rows_with_spaces['example'].astype(str).str.strip() == '')
            ]

            # remove duplicate rows by rank
            rows_with_spaces_no_examples = rows_with_spaces_no_examples.drop_duplicates(subset=['rank'])
            
            rows_processed = len(df)
            rows_with_spaces_count = len(rows_with_spaces)
            rows_excluded = rows_with_spaces_count - len(rows_with_spaces_no_examples)
            rows_found = len(rows_with_spaces_no_examples)
            
            total_rows_processed += rows_processed
            total_rows_with_spaces += rows_with_spaces_count
            total_rows_excluded += rows_excluded
            
            print(f"  Total rows: {rows_processed}")
            print(f"  Rows with spaces in definition: {rows_with_spaces_count}")
            print(f"  Rows excluded (have examples): {rows_excluded}")
            print(f"  Rows to fix (spaces + no examples): {rows_found}")
            
            # Save the filtered rows to output file
            if rows_found > 0:
                rows_with_spaces_no_examples.to_csv(output_path, index=False)
                print(f"  Saved to: {output_path}")
            else:
                print(f"  No rows to fix found - skipping output file")
                
        except Exception as e:
            print(f"  Error processing {csv_file}: {str(e)}")
            continue
    
    print(f"\n=== SUMMARY ===")
    print(f"Total rows processed: {total_rows_processed:,}")
    print(f"Total rows with spaces in definition: {total_rows_with_spaces:,}")
    print(f"Total rows excluded (have examples): {total_rows_excluded:,}")
    print(f"Total rows to fix (spaces + no examples): {total_rows_with_spaces - total_rows_excluded:,}")
    print(f"Files processed: {len(csv_files)}")

def main():
    """Main function to run the script."""
    
    # Define paths
    input_directory = "jjhy_csv/final_merged"
    output_directory = "jjhy_csv/tofixdefinition"
    
    print("Starting to find definitions with spaces (excluding rows with examples)...")
    print(f"Input directory: {input_directory}")
    print(f"Output directory: {output_directory}")
    
    # Check if input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: Input directory '{input_directory}' does not exist!")
        return
    
    # Process the files
    find_definitions_with_spaces(input_directory, output_directory)
    
    print("\nScript completed!")

if __name__ == "__main__":
    main()
