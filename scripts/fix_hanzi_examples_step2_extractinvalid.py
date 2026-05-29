import pandas as pd
import os

def extract_invalid_rows():
    # Path to the CSV file
    input_file = "others/hanzi_examples_validation_QW.csv"
    output_file = "others/hanzi_examples_validation_QW_invalid.csv"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found!")
        return
    
    print(f"Reading file: {input_file}")
    
    # Read the CSV file in chunks to handle large files efficiently
    chunk_size = 10000
    invalid_rows = []
    
    try:
        # Read the first few rows to get column names
        sample_df = pd.read_csv(input_file, nrows=5, dtype=str)
        print(f"Columns found: {list(sample_df.columns)}")
        
        # Check if 'is_valid' column exists
        if 'is_valid' not in sample_df.columns:
            print("Error: 'is_valid' column not found in the CSV file!")
            print(f"Available columns: {list(sample_df.columns)}")
            return
        
        # Read the file in chunks
        for chunk_num, chunk in enumerate(pd.read_csv(input_file, chunksize=chunk_size, dtype=str)):
            print(f"Processing chunk {chunk_num + 1}...")
            
            # Filter rows where is_valid is False
            invalid_chunk = chunk[chunk['is_valid'] == 'False']
            
            if not invalid_chunk.empty:
                invalid_rows.append(invalid_chunk)
        
        if invalid_rows:
            # Combine all invalid rows
            all_invalid = pd.concat(invalid_rows, ignore_index=True)
            
            # Remove the correct_example column
            all_invalid = all_invalid.drop(columns=['correct_example'])

            # Save to output file
            all_invalid.to_csv(output_file, index=False)
            
            print(f"\nExtraction completed!")
            print(f"Total invalid rows found: {len(all_invalid)}")
            print(f"Output saved to: {output_file}")
            
            # Show first few rows as preview
            print(f"\nFirst 5 invalid rows:")
            print(all_invalid.head())
            
        else:
            print("No invalid rows found (is_valid = False)")
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    extract_invalid_rows() 