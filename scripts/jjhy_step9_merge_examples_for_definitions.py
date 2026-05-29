#!/usr/bin/env python3
"""
Script to merge examples for the same definition in JJHY parsed CSV files.
This script processes files in jjhy_csv/script_parsed_csv/ and merges examples
for rows that have identical definitions, similar to the format in jjhy_csv/llm_parsed_csv/.
"""

import pandas as pd
import os
import sys
from pathlib import Path

def merge_examples_for_file(input_file_path, output_file_path):
    """
    Merge examples for rows with identical definitions.
    
    Args:
        input_file_path (str): Path to input CSV file
        output_file_path (str): Path to output CSV file
    """
    print(f"Processing: {input_file_path}")
    
    # Read the CSV file
    try:
        df = pd.read_csv(input_file_path)
    except Exception as e:
        print(f"Error reading {input_file_path}: {e}")
        return False
    
    print(f"Original rows: {len(df)}")
    
    # Add original order index to preserve ordering
    df['_original_order'] = range(len(df))
    
    # Define the columns to group by (all columns except 'example' and '_original_order')
    group_columns = [col for col in df.columns if col not in ['example', '_original_order']]
    
    # Group by all columns except 'example' and merge examples
    def merge_examples(group):
        # Sort by original order to preserve sequence
        group = group.sort_values('_original_order')
        
        # Filter out empty examples and merge with ｜ separator
        examples = group['example'].fillna('').astype(str)
        examples = examples[examples != '']  # Remove empty strings but keep order
        
        if len(examples) > 0:
            merged_example = '｜'.join(examples)
        else:
            merged_example = ''
        
        # Return the first row (in original order) with merged examples
        result = group.iloc[0].copy()
        result['example'] = merged_example.replace(' ', '')
        return result
    
    # Group and merge
    grouped = df.groupby(group_columns, dropna=False)
    merged_rows = []
    
    for name, group in grouped:
        merged_row = merge_examples(group)
        merged_rows.append(merged_row.to_dict())
    
    # Create DataFrame from merged rows
    merged_df = pd.DataFrame(merged_rows)
    
    # Sort by original order to maintain overall sequence
    merged_df = merged_df.sort_values('_original_order').reset_index(drop=True)
    
    # Remove the temporary order column
    merged_df = merged_df.drop('_original_order', axis=1)
    
    # Add sequence number (sn) column
    # Group by hanzi/cihui to assign sequence numbers for each character/word
    if 'cihui' in merged_df.columns:
        # For cihui files
        merged_df['sn'] = merged_df.groupby(['rank', 'cihui']).cumcount() + 1
        # Reorder columns to put sn between rank and cihui
        cols = ['rank', 'sn', 'cihui'] + [col for col in merged_df.columns if col not in ['rank', 'sn', 'cihui']]
    elif 'hanzi' in merged_df.columns:
        # For hanzi files
        merged_df['sn'] = merged_df.groupby(['rank', 'hanzi']).cumcount() + 1
        # Reorder columns to put sn between rank and hanzi
        cols = ['rank', 'sn', 'hanzi'] + [col for col in merged_df.columns if col not in ['rank', 'sn', 'hanzi']]
    else:
        # Fallback: just add sn as second column
        merged_df['sn'] = range(1, len(merged_df) + 1)
        cols = [merged_df.columns[0], 'sn'] + [col for col in merged_df.columns if col not in [merged_df.columns[0], 'sn']]
    
    merged_df = merged_df[cols]
    
    print(f"Merged rows: {len(merged_df)}")
    print(f"Reduction: {len(df) - len(merged_df)} rows ({((len(df) - len(merged_df)) / len(df) * 100):.1f}%)")
    
    # Save the merged data
    try:
        merged_df.to_csv(output_file_path, index=False)
        print(f"Saved to: {output_file_path}")
        return True
    except Exception as e:
        print(f"Error saving {output_file_path}: {e}")
        return False

def main():
    """Main function to process all files in script_parsed_csv directory."""
    
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    input_dir = project_root / "jjhy_csv" / "script_parsed_csv"
    output_dir = project_root / "jjhy_csv" / "script_parsed_csv_merged"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Get all CSV files in the input directory
    csv_files = list(input_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 60)
    
    successful = 0
    failed = 0
    
    for csv_file in sorted(csv_files):
        input_file_path = csv_file
        output_file_path = output_dir / csv_file.name
        
        if merge_examples_for_file(input_file_path, output_file_path):
            successful += 1
        else:
            failed += 1
        
        print("-" * 60)
    
    print(f"\nProcessing complete!")
    print(f"Successfully processed: {successful} files")
    print(f"Failed: {failed} files")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    main()
