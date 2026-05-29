#!/usr/bin/env python3
"""
Script to update core CSV files with corresponding rows from ref_definitions_replaced files.
For each file in jjhy_csv/core_csv, finds matching rows in jjhy_csv/ref_definitions_replaced/
based on rank and sn values, and updates the core file.
"""

import os
import pandas as pd
import glob
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_core_csv.log'),
        logging.StreamHandler()
    ]
)

def get_corresponding_files():
    """Get pairs of core and ref_definitions_replaced files."""
    core_dir = Path("jjhy_csv/core_csv")
    ref_dir = Path("jjhy_csv/ref_definitions_replaced")
    
    if not core_dir.exists():
        raise FileNotFoundError(f"Core directory not found: {core_dir}")
    if not ref_dir.exists():
        raise FileNotFoundError(f"Ref definitions directory not found: {ref_dir}")
    
    # Get all CSV files in core directory
    core_files = list(core_dir.glob("*.csv"))
    
    file_pairs = []
    for core_file in core_files:
        ref_file = ref_dir / core_file.name
        if ref_file.exists():
            file_pairs.append((core_file, ref_file))
            logging.info(f"Found pair: {core_file.name}")
        else:
            logging.warning(f"No corresponding ref file found for: {core_file.name}")
    
    return file_pairs

def update_core_file(core_file_path, ref_file_path):
    """Update a single core file with data from its corresponding ref file."""
    try:
        logging.info(f"Processing: {core_file_path.name}")
        
        # Read the files
        core_df = pd.read_csv(core_file_path)
        ref_df = pd.read_csv(ref_file_path)
        
        logging.info(f"Core file: {len(core_df)} rows, Ref file: {len(ref_df)} rows")
        
        # Create a composite key for matching (rank + sn)
        core_df['composite_key'] = core_df['rank'].astype(str) + '_' + core_df['sn'].astype(str)
        ref_df['composite_key'] = ref_df['rank'].astype(str) + '_' + ref_df['sn'].astype(str)
        
        # Create a mapping from composite key to ref data
        ref_mapping = {}
        for _, row in ref_df.iterrows():
            key = row['composite_key']
            ref_mapping[key] = row
        
        # Update core file with ref data
        updated_count = 0
        for idx, row in core_df.iterrows():
            key = row['composite_key']
            if key in ref_mapping:
                ref_row = ref_mapping[key]
                # Update the relevant columns (keeping rank and sn unchanged)
                for col in ['cihui', 'pinyin', 'ref_hanzi', 'ref_pinyin', 'pos', 'definition', 'example']:
                    if col in ref_row and pd.notna(ref_row[col]):
                        core_df.at[idx, col] = ref_row[col]
                updated_count += 1
        
        # Remove the temporary composite key column
        core_df = core_df.drop('composite_key', axis=1)
        
        # Save the updated core file
        core_df.to_csv(core_file_path, index=False)
        
        logging.info(f"Updated {updated_count} rows in {core_file_path.name}")
        return updated_count
        
    except Exception as e:
        logging.error(f"Error processing {core_file_path.name}: {str(e)}")
        return 0

def main():
    """Main function to process all file pairs."""
    try:
        logging.info("Starting core CSV update process...")
        
        # Get file pairs
        file_pairs = get_corresponding_files()
        
        if not file_pairs:
            logging.warning("No file pairs found to process")
            return
        
        logging.info(f"Found {len(file_pairs)} file pairs to process")
        
        # Process each pair
        total_updated = 0
        for core_file, ref_file in file_pairs:
            updated_count = update_core_file(core_file, ref_file)
            total_updated += updated_count
        
        logging.info(f"Process completed. Total rows updated: {total_updated}")
        
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
