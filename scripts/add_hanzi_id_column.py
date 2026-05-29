import pandas as pd
import os

def add_hanzi_id_column():
    # Read the CSV file
    csv_path = "database_csv/hanzi_pinyin_v7_with_sn_updated.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found!")
        return
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Create the new hanzi_id column with values from frequency_rank as integers
    df.insert(0, 'hanzi_id', df['frequency_rank'].astype(int))
    
    # Save the modified DataFrame back to the CSV file
    df.to_csv(csv_path, index=False)
    
    print(f"Successfully added 'hanzi_id' column to {csv_path}")
    print(f"Total rows processed: {len(df)}")
    print(f"First few rows:")
    print(df.head())

if __name__ == "__main__":
    add_hanzi_id_column() 