#!/usr/bin/env python3
"""
Script to sort CSV data by root_sn then parent_sn then item_rank
"""

import pandas as pd
import os
import sys

def sort_csv_data(input_file, output_file=None):
    """
    Sort CSV data by root_sn then parent_sn then item_rank
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file (optional, defaults to adding '_sorted' suffix)
    """
    try:
        # Read the CSV file
        print(f"Reading CSV file: {input_file}")
        df = pd.read_csv(input_file)
        
        # Check if required columns exist
        required_columns = ['root_sn', 'parent_sn', 'item_rank']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            print(f"Available columns: {list(df.columns)}")
            return False
        
        # Display current data info
        print(f"Original data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Convert sn columns to integers
        sn_columns = ['root_sn', 'parent_sn', 'sn', 'item_rank']
        existing_sn_columns = [col for col in sn_columns if col in df.columns]
        
        print(f"Converting columns to integers: {existing_sn_columns}")
        for col in existing_sn_columns:
            # Handle potential NaN values and convert to int
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Sort by root_sn first, then parent_sn, then by item_rank
        print("Sorting data by root_sn then parent_sn then item_rank...")
        df_sorted = df.sort_values(['root_sn', 'parent_sn', 'item_rank'], ascending=[True, True, True])
        
        # Generate output filename if not provided
        if output_file is None:
            input_dir = os.path.dirname(input_file)
            input_name = os.path.splitext(os.path.basename(input_file))[0]
            input_ext = os.path.splitext(input_file)[1]
            output_file = os.path.join(input_dir, f"{input_name}_sorted{input_ext}")
        
        # Save sorted data
        print(f"Saving sorted data to: {output_file}")
        df_sorted.to_csv(output_file, index=False, encoding='utf-8')
        
        # Display summary
        print(f"Successfully sorted {len(df_sorted)} rows")
        print(f"Sorted data saved to: {output_file}")
        
        # Show first few rows of sorted data
        print("\nFirst 10 rows of sorted data:")
        print(df_sorted.head(10).to_string(index=False))
        
        return True
        
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        return False
    except pd.errors.EmptyDataError:
        print(f"Error: Empty CSV file: {input_file}")
        return False
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return False

def main():
    """Main function to handle command line arguments and execute sorting"""
    
    # Default input file (current file from context)
    default_input = r"c:\Users\NeonZeng\AppData\Local\HanziUpDataNext\jjhy_csv\topic\hanzi_topic_manual_selected_v2.csv"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = default_input
        print(f"Using default input file: {input_file}")
    
    # Optional output file
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file does not exist: {input_file}")
        return 1
    
    # Sort the data
    success = sort_csv_data(input_file, output_file)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
