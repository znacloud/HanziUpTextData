#!/usr/bin/env python3
"""
Script to merge and sort JJHY CSV files by type:
1. Merge all pinyin files and sort by pinyin_id
2. Merge all definition files and sort by definition_id  
3. Merge all examples files and sort by example_id
"""

import os
import pandas as pd
import glob
from pathlib import Path

def merge_and_sort_csv_files():
    """Merge and sort CSV files by type"""
    
    # Define source and output directories
    source_dir = "jjhy_csv/core_csv_seperated"
    output_dir = "database_csv"
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("Starting CSV file merging and sorting process...")
    
    # 1. Merge pinyin files and sort by pinyin_id
    print("\n1. Processing pinyin files...")
    pinyin_files = glob.glob(os.path.join(source_dir, "*pinyin*.csv"))
    pinyin_files.sort()  # Sort files by name for consistent ordering
    
    if pinyin_files:
        print(f"Found {len(pinyin_files)} pinyin files")
        pinyin_dfs = []
        
        for file_path in pinyin_files:
            print(f"  Reading: {os.path.basename(file_path)}")
            try:
                df = pd.read_csv(file_path, dtype= {'hsk_level': 'str'})
                pinyin_dfs.append(df)
            except Exception as e:
                print(f"    Error reading {file_path}: {e}")
                continue
        
        if pinyin_dfs:
            # Merge all pinyin dataframes
            merged_pinyin = pd.concat(pinyin_dfs, ignore_index=True)
            print(f"  Total pinyin records: {len(merged_pinyin)}")
            
            # Sort by pinyin_id
            if 'pinyin_id' in merged_pinyin.columns:
                merged_pinyin = merged_pinyin.sort_values('pinyin_id')
                print("  Sorted by pinyin_id")
            else:
                print("  Warning: pinyin_id column not found")
            
            # Save merged pinyin file
            output_file = os.path.join(output_dir, "jjhy_core_hanzi_pinyin.csv")
            merged_pinyin.to_csv(output_file, index=False)
            print(f"  Saved: {output_file}")
        else:
            print("  No pinyin data to merge")
    else:
        print("  No pinyin files found")
    
    # 2. Merge definition files and sort by definition_id
    print("\n2. Processing definition files...")
    definition_files = glob.glob(os.path.join(source_dir, "*definition*.csv"))
    definition_files.sort()  # Sort files by name for consistent ordering
    
    if definition_files:
        print(f"Found {len(definition_files)} definition files")
        definition_dfs = []
        
        for file_path in definition_files:
            print(f"  Reading: {os.path.basename(file_path)}")
            try:
                df = pd.read_csv(file_path)
                definition_dfs.append(df)
            except Exception as e:
                print(f"    Error reading {file_path}: {e}")
                continue
        
        if definition_dfs:
            # Merge all definition dataframes
            merged_definition = pd.concat(definition_dfs, ignore_index=True)
            print(f"  Total definition records: {len(merged_definition)}")
            
            # Sort by definition_id
            if 'definition_id' in merged_definition.columns:
                merged_definition = merged_definition.sort_values('definition_id')
                print("  Sorted by definition_id")
            else:
                print("  Warning: definition_id column not found")
            
            # Save merged definition file
            output_file = os.path.join(output_dir, "jjhy_core_hanzi_definition.csv")
            merged_definition.to_csv(output_file, index=False)
            print(f"  Saved: {output_file}")
        else:
            print("  No definition data to merge")
    else:
        print("  No definition files found")
    
    # 3. Merge examples files and sort by example_id
    print("\n3. Processing examples files...")
    examples_files = glob.glob(os.path.join(source_dir, "*examples*.csv"))
    examples_files.sort()  # Sort files by name for consistent ordering
    
    if examples_files:
        print(f"Found {len(examples_files)} examples files")
        examples_dfs = []
        
        for file_path in examples_files:
            print(f"  Reading: {os.path.basename(file_path)}")
            try:
                df = pd.read_csv(file_path)
                examples_dfs.append(df)
            except Exception as e:
                print(f"    Error reading {file_path}: {e}")
                continue
        
        if examples_dfs:
            # Merge all examples dataframes
            merged_examples = pd.concat(examples_dfs, ignore_index=True)
            print(f"  Total examples records: {len(merged_examples)}")
            
            # Sort by example_id
            if 'example_id' in merged_examples.columns:
                merged_examples = merged_examples.sort_values('example_id')
                print("  Sorted by example_id")
            else:
                print("  Warning: example_id column not found")
            
            # Save merged examples file
            output_file = os.path.join(output_dir, "jjhy_core_hanzi_example.csv")
            merged_examples.to_csv(output_file, index=False)
            print(f"  Saved: {output_file}")
        else:
            print("  No examples data to merge")
    else:
        print("  No examples files found")
    
    print("\nCSV file merging and sorting completed!")

if __name__ == "__main__":
    merge_and_sort_csv_files()
