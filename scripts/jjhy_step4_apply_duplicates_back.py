#!/usr/bin/env python3
"""
Script to apply duplicate rows from jjhy_hanzi_parsed_duplicate.csv back to the original parsed files.
This script uses the same composite key approach as jjhy_step3_extract_duplicate.py to match rows
and replace them with the duplicate entries in their original positions.
"""

import pandas as pd
import os
from pathlib import Path

def main():
    # Define file paths
    duplicate_file = "others/jjhy_hanzi_parsed_duplicate.csv"
    files_to_update = [
        "others/jjhy_hanzi_parsed_3500.csv",
        "others/jjhy_hanzi_parsed_5500.csv", 
        "others/jjhy_hanzi_parsed_6800.csv"
    ]
    
    print("Starting duplicate application process...")
    
    # Check if duplicate file exists
    if not os.path.exists(duplicate_file):
        print(f"Error: Duplicate file {duplicate_file} not found!")
        return
    
    # Read the duplicate file
    print(f"Reading duplicate file: {duplicate_file}")
    try:
        duplicates_df = pd.read_csv(duplicate_file, dtype=str)
        print(f"Loaded {len(duplicates_df)} duplicate rows")
    except Exception as e:
        print(f"Error reading duplicate file: {e}")
        return
    
    # Reorder columns in duplicates to match original file structure
    # Original: rank,hanzi,pinyin,ref_hanzi,ref_pinyin,pos,definition,example
    # Duplicate: rank,hanzi,pinyin,ref_pinyin,ref_hanzi,pos,definition,example
    reordered_duplicates = duplicates_df.copy()
    reordered_duplicates = reordered_duplicates[[
        'rank', 'hanzi', 'pinyin', 'ref_hanzi', 'ref_pinyin', 'pos', 'definition', 'example'
    ]]
    
    # Create composite key for duplicates (same as reference script)
    reordered_duplicates['composite_key'] = reordered_duplicates['hanzi'].astype(str) + '|' + \
                                           reordered_duplicates['pinyin'].astype(str) + '|' + \
                                           reordered_duplicates['definition'].astype(str) + '|' + \
                                           reordered_duplicates['example'].astype(str)
    
    # Check if all target files exist
    for file_path in files_to_update:
        if not os.path.exists(file_path):
            print(f"Warning: Target file {file_path} not found!")
    
    # Process each target file
    for file_path in files_to_update:
        if not os.path.exists(file_path):
            continue
            
        print(f"\nProcessing {file_path}...")
        
        try:
            # Read the original file
            original_df = pd.read_csv(file_path, dtype=str)
            print(f"  Original file has {len(original_df)} rows")
            
            # Get the rank range for this file
            min_rank = original_df['rank'].min()
            max_rank = original_df['rank'].max()
            print(f"  Rank range: {min_rank} - {max_rank}")
            
            # Filter duplicates that belong to this file's rank range
            file_duplicates = reordered_duplicates[
                (reordered_duplicates['rank'] >= min_rank) & 
                (reordered_duplicates['rank'] <= max_rank)
            ]
            
            if len(file_duplicates) == 0:
                print(f"  No duplicates found for rank range {min_rank}-{max_rank}")
                continue
            
            print(f"  Found {len(file_duplicates)} duplicates for this file")
            
            # Create composite key for original file (same as reference script)
            original_df['composite_key'] = original_df['hanzi'].astype(str) + '|' + \
                                         original_df['pinyin'].astype(str) + '|' + \
                                         original_df['definition'].astype(str) + '|' + \
                                         original_df['example'].astype(str)
            
            # Create a mapping of composite keys to duplicate rows
            duplicate_mapping = {}
            remove_mapping = {}
            for idx, row in file_duplicates.iterrows():
                key = row['composite_key']
                remove_key = f"{row['hanzi']}|{row['ref_pinyin']}|{row['definition']}|{row['example']}"
                remove_mapping[remove_key] = row['rank']
                if key not in duplicate_mapping:
                    duplicate_mapping[key] = []
                duplicate_mapping[key].append(row)
                
            
            # Create a new dataframe to hold the updated data
            updated_rows = []
            replaced_count = 0
            
            # Process each row in the original file to maintain order
            for idx, row in original_df.iterrows():
                key = row['composite_key']
                if key in duplicate_mapping:
                    # This row has duplicates, replace with all duplicate versions
                    for dup_row in duplicate_mapping[key]:
                        # Create a new row with the duplicate data
                        new_row = dup_row.copy()
                        new_row = new_row.drop('composite_key')
                        updated_rows.append(new_row)
                    replaced_count += 1
                    print(f"    Replaced row {idx}: {row['hanzi']} ({row['pinyin']}) with {len(duplicate_mapping[key])} duplicate versions")
                elif key not in remove_mapping:
                    # This row has no duplicates, keep as is
                    new_row = row.copy()
                    new_row = new_row.drop('composite_key')
                    updated_rows.append(new_row)
            
            # Create the updated dataframe
            updated_df = pd.DataFrame(updated_rows)
            
            # Sort by rank, then by other columns for consistent ordering
            # updated_df = updated_df.sort_values(['rank', 'hanzi', 'pinyin', 'definition', 'example'])
            # original_df = original_df.sort_values(['rank', 'hanzi', 'pinyin', 'definition', 'example']) 
            # Create backup of original file
            backup_path = file_path.replace('.csv', '_backup.csv')
            original_df.drop('composite_key', axis=1).to_csv(backup_path, index=False)
            print(f"  Created backup: {backup_path}")
            
            # Save the updated file
            updated_df.to_csv(file_path, index=False)
            print(f"  Updated file with {len(updated_df)} total rows")
            print(f"  Replaced {replaced_count} original rows with their duplicate versions")
            
            # Show some examples of replaced duplicates
            print(f"  Sample of replaced duplicates:")
            sample_duplicates = file_duplicates.head(3)
            for idx, row in sample_duplicates.iterrows():
                print(f"    Rank {row['rank']}: {row['hanzi']} ({row['pinyin']}) - {row['definition'][:50]}...")
            
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
            continue
    
    print("\nDuplicate application process completed!")
    print("Backup files have been created with '_backup' suffix.")

if __name__ == "__main__":
    main() 