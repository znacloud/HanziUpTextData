#!/usr/bin/env python3
"""
Script to filter JJHY CSV files based on whether the hanzi/cihui exists in reference files.
For each file in "jjhy_csv/final_merged/" dir, if the hanzi/cihui in each row exists in 
"raw_data/hsk_word.csv" or "raw_data/现代汉语常用词表_2008_sorted.csv", then keep that row.
Save the filtered result as the same-name file but in "jjhy_csv/core_csv/" directory.
"""

import os
import pandas as pd
import glob
from pathlib import Path

def load_reference_data():
    """Load the reference HSK word list and modern Chinese vocabulary list."""
    print("Loading reference data...")
    
    # Load HSK word list
    hsk_df = pd.read_csv('raw_data/hsk_word.csv')
    hsk_cihui_set = set(hsk_df['cihui'].dropna().unique())
    print(f"Loaded {len(hsk_cihui_set)} unique HSK cihui")
    
    # Load modern Chinese vocabulary list
    modern_df = pd.read_csv('raw_data/现代汉语常用词表_2008_sorted.csv')
    modern_cihui_set = set(modern_df['cihui'].dropna().unique())
    print(f"Loaded {len(modern_cihui_set)} unique modern Chinese cihui")
    
    # Combine both sets
    all_reference_cihui = hsk_cihui_set.union(modern_cihui_set)
    print(f"Total unique reference cihui: {len(all_reference_cihui)}")
    
    return all_reference_cihui

def filter_file(input_file_path, output_file_path, reference_cihui_set):
    """Filter a single CSV file based on reference cihui set."""
    print(f"Processing: {os.path.basename(input_file_path)}")
    
    # Read the CSV file
    df = pd.read_csv(input_file_path)
    original_count = len(df)
    
    # Determine the column to check based on file content
    if 'cihui' in df.columns:
        # This is a cihui file
        check_column = 'cihui'
        print(f"  - Detected cihui file with {original_count} rows")
    elif 'hanzi' in df.columns:
        # This is a hanzi file
        check_column = 'hanzi'
        print(f"  - Detected hanzi file with {original_count} rows")
    else:
        print(f"  - Warning: Could not determine file type for {input_file_path}")
        return
    
    # Filter rows where the cihui/hanzi exists in reference set
    filtered_df = df[df[check_column].isin(reference_cihui_set)]
    filtered_count = len(filtered_df)
    
    print(f"  - Kept {filtered_count} rows out of {original_count} ({(filtered_count/original_count)*100:.1f}%)")
    
    # Save filtered result
    filtered_df.to_csv(output_file_path, index=False)
    print(f"  - Saved to: {output_file_path}")
    
    return filtered_count, original_count

def main():
    """Main function to process all files."""
    # Create output directory if it doesn't exist
    output_dir = Path('jjhy_csv/core_csv/')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load reference data
    reference_cihui_set = load_reference_data()
    
    # Get all CSV files in the final_merged directory
    input_dir = 'jjhy_csv/final_merged/'
    csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
    
    print(f"\nFound {len(csv_files)} CSV files to process")
    print("=" * 60)
    
    # Process each file
    total_original = 0
    total_filtered = 0
    
    for input_file in sorted(csv_files):
        filename = os.path.basename(input_file)
        output_file = output_dir / filename
        
        try:
            filtered_count, original_count = filter_file(input_file, output_file, reference_cihui_set)
            total_original += original_count
            total_filtered += filtered_count
        except Exception as e:
            print(f"  - Error processing {filename}: {e}")
    
    print("=" * 60)
    print(f"Processing complete!")
    print(f"Total original rows: {total_original:,}")
    print(f"Total filtered rows: {total_filtered:,}")
    print(f"Overall retention rate: {(total_filtered/total_original)*100:.1f}%")
    print(f"Filtered files saved to: {output_dir.absolute()}")

if __name__ == "__main__":
    main()
