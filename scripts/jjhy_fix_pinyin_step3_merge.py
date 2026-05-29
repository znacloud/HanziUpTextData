#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to merge jjhy_pinyin_cleaned.csv and jjhy_pinyin_spaced_fixed.csv
based on term,pinyin pairs to create jjhy_pinyin_final.csv
"""

import pandas as pd
import os
from pathlib import Path

def merge_pinyin_files():
    # Define file paths
    base_dir = Path("jjhy_csv/core_pinyin")
    cleaned_file = base_dir / "jjhy_pinyin_cleaned.csv"
    spaced_file = base_dir / "jjhy_pinyin_spaced_fixed.csv"
    output_file = base_dir / "jjhy_pinyin_final.csv"
    
    print(f"Reading {cleaned_file}...")
    # Read the cleaned file
    try:
        cleaned_df = pd.read_csv(cleaned_file, encoding='utf-8')
        print(f"Successfully read {cleaned_file}: {len(cleaned_df)} rows")
    except UnicodeDecodeError:
        # Try different encodings if UTF-8 fails
        try:
            cleaned_df = pd.read_csv(cleaned_file, encoding='gbk')
            print(f"Successfully read {cleaned_file} with GBK encoding: {len(cleaned_df)} rows")
        except:
            cleaned_df = pd.read_csv(cleaned_file, encoding='latin1')
            print(f"Successfully read {cleaned_file} with Latin1 encoding: {len(cleaned_df)} rows")
    
    print(f"Reading {spaced_file}...")
    # Read the spaced file
    try:
        spaced_df = pd.read_csv(spaced_file, encoding='utf-8')
        print(f"Successfully read {spaced_file}: {len(spaced_df)} rows")
    except UnicodeDecodeError:
        # Try different encodings if UTF-8 fails
        try:
            spaced_df = pd.read_csv(spaced_file, encoding='gbk')
            print(f"Successfully read {spaced_file} with GBK encoding: {len(spaced_df)} rows")
        except:
            spaced_df = pd.read_csv(spaced_file, encoding='latin1')
            print(f"Successfully read {spaced_file} with Latin1 encoding: {len(spaced_df)} rows")
    
    # Display column names for debugging
    print(f"\nCleaned file columns: {list(cleaned_df.columns)}")
    print(f"Spaced file columns: {list(spaced_df.columns)}")
    
    # Display first few rows for debugging
    print(f"\nFirst few rows of cleaned file:")
    print(cleaned_df.head())
    print(f"\nFirst few rows of spaced file:")
    print(spaced_df.head())
    
    # Create a mapping dictionary from spaced_file
    # Use term + cleaned_pinyin as the key to match with cleaned_file
    print("\nCreating mapping...")
    
    # Create a composite key for mapping
    spaced_df['composite_key'] = spaced_df['term'] + '|' + spaced_df['cleaned_pinyin']
    
    # Create the mapping dictionary
    mapping_updated_dict = dict(zip(spaced_df['composite_key'], spaced_df['updated_pinyin']))
    
    print(f"Created mapping with {len(mapping_updated_dict)} entries")
    
    # Apply the mapping to create the final dataframe
    print("Applying mapping...")
    
    # Initialize the result dataframe
    result_df = cleaned_df.copy()
    result_df['updated_pinyin'] = ''
    
    # Apply mapping
    matched_count = 0
    for idx, row in result_df.iterrows():
        composite_key = row['term'] + '|' + row['cleaned_pinyin']
        if composite_key in mapping_updated_dict:
            result_df.at[idx, 'updated_pinyin'] = mapping_updated_dict[composite_key]
            matched_count += 1
        else:
            # If no match found, use the original pinyin
            raise ValueError(f"No match found for {composite_key}")
    
    print(f"Matched {matched_count} out of {len(result_df)} rows")
    
    # Remove the composite_key columns if they exist
    if 'composite_key' in result_df.columns:
        result_df = result_df.drop('composite_key', axis=1)
    
    # Save the result
    print(f"Saving result to {output_file}...")
    result_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Successfully created {output_file} with {len(result_df)} rows")
    print(f"Columns: {list(result_df.columns)}")
    
    # Display sample of the result
    print(f"\nSample of final result:")
    print(result_df.head(10))
    
    return result_df

if __name__ == "__main__":
    try:
        result = merge_pinyin_files()
        print("\nScript completed successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
