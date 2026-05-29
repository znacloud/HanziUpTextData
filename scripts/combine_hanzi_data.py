#!/usr/bin/env python3
"""
Script to combine hanzi data from multiple CSV files.
Combines definition, pinyin, and example data into a single CSV file using proper joins.
"""

import pandas as pd
import os

def main():
    # File paths
    definition_file = "database_csv/hanzi_definition_v7_with_pos_updated.csv"
    pinyin_file = "database_csv/hanzi_pinyin_v7_with_sn_updated.csv"
    example_file = "database_csv/hanzi_examples_v7.csv"
    output_file = "others/all_hanzi_pinyin_definition_example.csv"
    
    # Check if input files exist
    for file_path in [definition_file, pinyin_file, example_file]:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found!")
            return
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print("Reading CSV files...")
    
    try:
        # Read definition data - select required columns
        df_definitions = pd.read_csv(definition_file)
        df_definitions = df_definitions[["definition_id", "pinyin_id", "definition_cn", "pos"]]
        print(f"Loaded {len(df_definitions)} definition records")
        
        # Read pinyin data - select required columns
        df_pinyin = pd.read_csv(pinyin_file)
        df_pinyin = df_pinyin[["pinyin_id", "hanzi", "pinyin"]]
        print(f"Loaded {len(df_pinyin)} pinyin records")
        
        # Read example data - select required columns
        df_examples = pd.read_csv(example_file)
        df_examples = df_examples[["definition_id", "example_cn"]]
        print(f"Loaded {len(df_examples)} example records")
        
    except Exception as e:
        print(f"Error reading CSV files: {e}")
        return
    
    print("Joining data...")
    
    # Step 1: Join definitions with pinyin data using pinyin_id
    print("Joining definitions with pinyin data...")
    df_combined = df_definitions.merge(
        df_pinyin, 
        on='pinyin_id', 
        how='left'
    )
    print(f"After joining with pinyin: {len(df_combined)} records")
    
    # Step 2: Join with examples data using definition_id
    print("Joining with examples data...")
    df_combined = df_combined.merge(
        df_examples, 
        on='definition_id', 
        how='left'
    )
    print(f"After joining with examples: {len(df_combined)} records")
    
    # Reorder columns to match the requested order
    final_columns = ["definition_id", "hanzi", "pinyin", "pos", "definition_cn", "example_cn"]
    df_final = df_combined[final_columns]
    
    # Remove duplicates if any
    df_final = df_final.drop_duplicates()
    print(f"Final dataset: {len(df_final)} unique records")

    # Remove rows where definition_cn OR example_cn is empty
    df_final = df_final[df_final['definition_cn'].notna() | df_final['example_cn'].notna()]
    print(f"Final dataset after removing empty definition_cn or example_cn rows: {len(df_final)} records")
    
    # Save the combined data
    try:
        df_final.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Successfully saved combined data to {output_file}")
        print(f"Output file contains {len(df_final)} rows and {len(df_final.columns)} columns")
        print("Columns:", list(df_final.columns))
        
        # Display first few rows as preview
        print("\nFirst 5 rows of combined data:")
        print(df_final.head())
        
        # Show some statistics
        print(f"\nStatistics:")
        print(f"- Records with hanzi: {df_final['hanzi'].notna().sum()}")
        print(f"- Records with pinyin: {df_final['pinyin'].notna().sum()}")
        print(f"- Records with examples: {df_final['example_cn'].notna().sum()}")
        
    except Exception as e:
        print(f"Error saving output file: {e}")

if __name__ == "__main__":
    main() 