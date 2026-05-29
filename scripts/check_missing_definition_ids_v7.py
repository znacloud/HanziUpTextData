import pandas as pd
import os

def check_missing_definition_ids():
    # File paths
    source_file = "database_csv/hanzi_definition_with_hanzi_pinyin_empty_ref.csv"
    target_file = "database_csv/hanzi_examples_v6_generated.csv"
    
    # Check if files exist
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found!")
        return
    if not os.path.exists(target_file):
        print(f"Error: Target file '{target_file}' not found!")
        return
    
    try:
        # Read the CSV files
        print("Reading source file...")
        source_df = pd.read_csv(source_file)
        print("Reading target file...")
        target_df = pd.read_csv(target_file)
        
        # Get the definition_ids from both files
        source_ids = set(source_df['definition_id'].unique())
        target_ids = set(target_df['definition_id'].unique())
        
        # Find missing definition_ids
        missing_ids = source_ids - target_ids
        
        # Print results
        print(f"\nTotal definition_ids in source file: {len(source_ids)}")
        print(f"Total definition_ids in target file: {len(target_ids)}")
        print(f"Number of missing definition_ids: {len(missing_ids)}")
        
        if missing_ids:
            print("\nMissing definition_ids:")
            print(f"[{', '.join(f"'{id}'" for id in sorted(missing_ids))}]")
            
            # Save missing IDs to a file
            # output_file = "missing_definition_ids.csv"
            # pd.DataFrame({'definition_id': sorted(missing_ids)}).to_csv(output_file, index=False)
            # print(f"\nMissing definition_ids have been saved to {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    check_missing_definition_ids() 