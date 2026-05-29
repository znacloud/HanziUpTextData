#!/usr/bin/env python3
"""
Script to filter rows from CSV files in jjhy_csv/core_csv/ 
whose definition column contains the pattern [①②③④⑤⑥⑦⑧⑨⑩][1-9]?
and save the filtered results to jjhy_csv/refdefinition/
"""

import os
import re
import pandas as pd
from pathlib import Path

def create_directory_if_not_exists(directory_path):
    """Create directory if it doesn't exist."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)
    print(f"Directory created/verified: {directory_path}")

def filter_csv_by_pattern(input_file_path, output_file_path, pattern):
    """
    Filter CSV file by pattern in definition column.
    
    Args:
        input_file_path (str): Path to input CSV file
        output_file_path (str): Path to output CSV file
        pattern (str): Regex pattern to search for
    """
    try:
        # Read the CSV file
        print(f"Processing: {input_file_path}")
        df = pd.read_csv(input_file_path)
        
        # Check if 'definition' column exists
        if 'definition' not in df.columns:
            print(f"Warning: 'definition' column not found in {input_file_path}")
            return False
        
        # Filter rows where definition contains the pattern
        # The pattern matches: [①②③④⑤⑥⑦⑧⑨⑩] followed by optional [1-9]
        mask = df['definition'].str.contains(pattern, regex=True, na=False)
        filtered_df = df[mask]
        
        # Save filtered results
        filtered_df.to_csv(output_file_path, index=False)
        
        print(f"  Filtered {len(filtered_df)} rows out of {len(df)} total rows")
        print(f"  Saved to: {output_file_path}")
        
        return True
        
    except Exception as e:
        print(f"Error processing {input_file_path}: {str(e)}")
        return False

def main():
    """Main function to process all CSV files."""
    # Define paths
    core_csv_dir = "jjhy_csv/core_csv"
    output_dir = "jjhy_csv/refdefinition"
    
    # Create output directory if it doesn't exist
    create_directory_if_not_exists(output_dir)
    
    # Define the pattern to search for
    # [①②③④⑤⑥⑦⑧⑨⑩] followed by optional [1-9]
    pattern = r'[①②③④⑤⑥⑦⑧⑨⑩][1-9]?'
    
    # Get all CSV files in the core_csv directory
    csv_files = [f for f in os.listdir(core_csv_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in {core_csv_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    print(f"Pattern to search for: {pattern}")
    print("-" * 50)
    
    # Process each CSV file
    successful_count = 0
    total_count = len(csv_files)
    
    for csv_file in sorted(csv_files):
        input_path = os.path.join(core_csv_dir, csv_file)
        output_path = os.path.join(output_dir, csv_file)
        
        if filter_csv_by_pattern(input_path, output_path, pattern):
            successful_count += 1
    
    print("-" * 50)
    print(f"Processing complete!")
    print(f"Successfully processed: {successful_count}/{total_count} files")
    print(f"Results saved to: {output_dir}")

if __name__ == "__main__":
    main()
