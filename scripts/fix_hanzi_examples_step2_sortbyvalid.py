import pandas as pd
import os
import sys

def sort_by_is_valid(input_file, output_file):
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found!")
        return
    
    print(f"Reading file: {input_file}")
    
    try:
        # Read the entire file with string dtype to handle mixed data types
        print("Loading data...")
        df = pd.read_csv(input_file, dtype=str)
        
        print(f"Total rows: {len(df)}")
        print(f"Columns found: {list(df.columns)}")
        
        # Check if 'is_valid' column exists
        if 'is_valid' not in df.columns:
            print("Error: 'is_valid' column not found in the CSV file!")
            print(f"Available columns: {list(df.columns)}")
            return
        
        # Count values in is_valid column
        valid_counts = df['is_valid'].value_counts()
        print(f"\nValue counts in 'is_valid' column:")
        print(valid_counts)
        
        # Sort by is_valid column (False values first, then True)
        # We'll sort in ascending order so False comes before True
        print("\nSorting rows by 'is_valid' column...")
        df_sorted = df.sort_values(by='is_valid', ascending=True)
        
        # Save sorted data to output file
        df_sorted.to_csv(output_file, index=False)
        
        print(f"\nSorting completed!")
        print(f"Output saved to: {output_file}")
        
        # Show first few rows as preview
        print(f"\nFirst 10 rows after sorting:")
        print(df_sorted.head(10))
        
        # Show the distribution after sorting
        print(f"\nValue counts after sorting:")
        print(df_sorted['is_valid'].value_counts())
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    # receive input/output file from command line
    # use default input/output file if not provided
    if len(sys.argv) < 3:
        input_file = "others/hanzi_examples_validation_QW.csv"
        output_file = "others/hanzi_examples_validation_QW_sorted.csv"
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    sort_by_is_valid(input_file, output_file) 