#!/usr/bin/env python3
"""
Script to merge files from jjhy_csv/llm_parsed_csv/ and jjhy_csv/script_parsed_csv_merged/
based on rank values. LLM parsed files take priority - if a rank exists in LLM file,
it overrides the corresponding rank in script parsed file.
"""

import pandas as pd
import os
import re
from pathlib import Path

def extract_base_name(filename):
    """Extract the base name to match files between directories."""
    # Convert jjhy_cihui_llm_parsed_5000_partial.csv -> jjhy_cihui_parsed_5000_filtered.csv
    # Convert jjhy_hanzi_llm_parsed_3500_partial.csv -> jjhy_hanzi_parsed_3500_filtered.csv
    
    if '_fixdefinition_parsed_' in filename and re.search(r'_\d+\.csv$', filename):
        # Replace _fixdefinition_parsed_ with _parsed_ and remove only the last number before .csv
        base_name = re.sub(r'_\d+\.csv$', '_filtered.csv', filename)
        base_name = base_name.replace('_fixdefinition_parsed_', '_parsed_')
        return base_name
    elif '_parsed_' in filename and filename.endswith('_filtered.csv'):
        # This is already a script parsed file name
        return filename
    else:
        return None

def merge_files(llm_file_path, script_file_path, output_file_path):
    """
    Merge LLM and script parsed files based on rank values.
    LLM file takes priority for overlapping ranks.
    """
    print(f"Merging:")
    print(f"  LLM file: {llm_file_path.name}")
    print(f"  Script file: {script_file_path.name}")
    
    try:
        # Read both files
        llm_df = pd.read_csv(llm_file_path)
        script_df = pd.read_csv(script_file_path)
        
        print(f"  LLM rows: {len(llm_df)}")
        print(f"  Script rows: {len(script_df)}")
        
        # Get the ranks that exist in LLM file
        llm_ranks = set(llm_df['rank'].unique())
        print(f"  LLM ranks to override: {sorted(llm_ranks)}")
        
        # Filter out the overlapping ranks from script file
        script_df_filtered = script_df[~script_df['rank'].isin(llm_ranks)]
        print(f"  Script rows after filtering: {len(script_df_filtered)}")
        
        # Combine the files: script (filtered) + llm
        merged_df = pd.concat([script_df_filtered, llm_df], ignore_index=True)
        
        # Sort by rank to maintain proper order
        merged_df = merged_df.sort_values(['rank', 'sn']).reset_index(drop=True)
        
        print(f"  Final merged rows: {len(merged_df)}")
        
        # Save the merged file
        merged_df.to_csv(output_file_path, index=False)
        print(f"  Saved to: {output_file_path}")
        
        return True
        
    except Exception as e:
        print(f"  Error merging files: {e}")
        return False

def main():
    """Main function to merge all matching files."""
    
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    llm_dir = project_root / "jjhy_csv" / "llm_parsed_csv"
    script_dir_path = project_root / "jjhy_csv" / "final_merged"
    output_dir = project_root / "jjhy_csv" / "final_merged"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    print(f"LLM directory: {llm_dir}")
    print(f"Script directory: {script_dir_path}")
    print(f"Output directory: {output_dir}")
    print("-" * 80)
    
    # Get all LLM files
    llm_files = list(llm_dir.glob("*.csv"))
    
    if not llm_files:
        print("No LLM files found!")
        return
    
    print(f"Found {len(llm_files)} LLM files to process")
    
    successful = 0
    failed = 0
    skipped = 0
    
    for llm_file in sorted(llm_files):
        # Find corresponding script file
        base_name = extract_base_name(llm_file.name)
        
        if not base_name:
            print(f"Skipping {llm_file.name} - cannot determine base name")
            skipped += 1
            continue
            
        script_file = script_dir_path / base_name
        
        if not script_file.exists():
            print(f"Skipping {llm_file.name} - no corresponding script file: {base_name}")
            skipped += 1
            continue
        
        # Determine output file name (same as script file name)
        output_file = output_dir / base_name
        
        # Merge the files
        if merge_files(llm_file, script_file, output_file):
            successful += 1
        else:
            failed += 1
        
        print("-" * 80)
    
    print(f"\nMerging complete!")
    print(f"Successfully merged: {successful} files")
    print(f"Failed: {failed} files")
    print(f"Skipped: {skipped} files")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    main()
