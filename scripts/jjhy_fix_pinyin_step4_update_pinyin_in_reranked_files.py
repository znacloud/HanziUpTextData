#!/usr/bin/env python3
"""
Script to update pinyin values with updated_pinyin values from the reference file.
For each file in jjhy_csv/core_csv_reranked/, replaces pinyin with updated_pinyin
using cihui/hanzi and pinyin as keys, and saves to core_csv_reranked_with_updated_pinyin/.
"""

import pandas as pd
import os
import sys
from pathlib import Path

def create_pinyin_mapping(reference_file_path):
    """
    Create a mapping from (term, pinyin) to updated_pinyin from the reference file.
    
    Args:
        reference_file_path (str): Path to the reference CSV file
        
    Returns:
        dict: Mapping from (term, pinyin) tuple to updated_pinyin string
    """
    print(f"Reading reference file: {reference_file_path}")
    
    try:
        # Read the reference file
        ref_df = pd.read_csv(reference_file_path)
        
        # Create mapping from (term, pinyin) to updated_pinyin
        pinyin_mapping = {}
        for _, row in ref_df.iterrows():
            term = row['term']
            pinyin = row['pinyin']
            updated_pinyin = row['updated_pinyin']
            
            # Use (term, pinyin) as key
            key = (term, pinyin)
            pinyin_mapping[key] = updated_pinyin
            
        print(f"Created mapping with {len(pinyin_mapping)} entries")
        return pinyin_mapping
        
    except Exception as e:
        print(f"Error reading reference file: {e}")
        return {}

def update_pinyin_in_file(input_file_path, output_file_path, pinyin_mapping):
    """
    Update pinyin values in a CSV file using the provided mapping.
    
    Args:
        input_file_path (str): Path to input CSV file
        output_file_path (str): Path to output CSV file
        pinyin_mapping (dict): Mapping from (term, pinyin) to updated_pinyin
    """
    print(f"Processing: {input_file_path}")
    
    try:
        # Read the input file
        df = pd.read_csv(input_file_path)
        
        # Determine which column to use based on filename
        filename = os.path.basename(input_file_path)
        if 'cihui' in filename:
            term_column = 'cihui'
        elif 'hanzi' in filename:
            term_column = 'hanzi'
        else:
            print(f"Warning: Cannot determine term column from filename: {filename}")
            return False
        
        # Check if required columns exist
        required_cols = [term_column, 'pinyin']
        if not all(col in df.columns for col in required_cols):
            print(f"Warning: Required columns {required_cols} not found in {input_file_path}")
            return False
            
        # Track changes
        changes_made = 0
        total_rows = len(df)
        
        # Update pinyin values
        for idx, row in df.iterrows():
            term = row[term_column]
            pinyin = row['pinyin']
            
            # Look up updated pinyin
            key = (term, pinyin)
            if key in pinyin_mapping:
                updated_pinyin = pinyin_mapping[key]
                if updated_pinyin != pinyin:
                    df.at[idx, 'pinyin'] = updated_pinyin
                    changes_made += 1
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save updated file
        df.to_csv(output_file_path, index=False)
        
        print(f"  Updated {changes_made}/{total_rows} rows using {term_column} column")
        print(f"  Saved to: {output_file_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {input_file_path}: {e}")
        return False

def main():
    """Main function to process all files."""
    
    # Define paths
    base_dir = "jjhy_csv"
    input_dir = os.path.join(base_dir, "core_csv_reranked")
    output_dir = os.path.join(base_dir, "core_csv_reranked_with_updated_pinyin")
    reference_file = os.path.join(base_dir, "core_pinyin", "jjhy_pinyin_final.csv")
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist")
        sys.exit(1)
        
    # Check if reference file exists
    if not os.path.exists(reference_file):
        print(f"Error: Reference file {reference_file} does not exist")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Create pinyin mapping
    pinyin_mapping = create_pinyin_mapping(reference_file)
    if not pinyin_mapping:
        print("Error: Failed to create pinyin mapping")
        sys.exit(1)
    
    # Get list of CSV files to process
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    csv_files.sort()
    
    # Categorize files by type
    cihui_files = [f for f in csv_files if 'cihui' in f]
    hanzi_files = [f for f in csv_files if 'hanzi' in f]
    
    print(f"\nFound {len(csv_files)} CSV files to process:")
    print(f"  Cihui files: {len(cihui_files)}")
    print(f"  Hanzi files: {len(hanzi_files)}")
    print(f"\nFiles:")
    for f in csv_files:
        file_type = "cihui" if 'cihui' in f else "hanzi" if 'hanzi' in f else "unknown"
        print(f"  - {f} ({file_type})")
    
    # Process each file
    print(f"\nProcessing files...")
    successful = 0
    failed = 0
    
    for csv_file in csv_files:
        input_path = os.path.join(input_dir, csv_file)
        output_path = os.path.join(output_dir, csv_file)
        
        if update_pinyin_in_file(input_path, output_path, pinyin_mapping):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\nProcessing complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(csv_files)}")

if __name__ == "__main__":
    main()
