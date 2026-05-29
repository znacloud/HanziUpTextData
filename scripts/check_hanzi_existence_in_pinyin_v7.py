import pandas as pd
import os

def check_hanzi_existence():
    # Define file paths
    frequency_file = os.path.join('database_csv', 'hanzi_frequency_filtered.csv')
    pinyin_file = os.path.join('database_csv', 'hanzi_pinyin_v7_with_sn_updated.csv')
    
    # Read the CSV files
    print("Reading CSV files...")
    frequency_df = pd.read_csv(frequency_file)
    pinyin_df = pd.read_csv(pinyin_file)
    
    # Get sets of hanzi characters
    frequency_hanzi = set(frequency_df['hanzi'])
    pinyin_hanzi = set(pinyin_df['hanzi'])
    
    # Find missing hanzi
    missing_hanzi = frequency_hanzi - pinyin_hanzi
    
    # Print results
    print(f"\nTotal hanzi in frequency file: {len(frequency_hanzi)}")
    print(f"Total hanzi in pinyin file: {len(pinyin_hanzi)}")
    print(f"Number of missing hanzi: {len(missing_hanzi)}")
    
    if missing_hanzi:
        # Get the rows for missing hanzi with their frequency information
        missing_df = frequency_df[frequency_df['hanzi'].isin(missing_hanzi)]
        missing_df = missing_df[['hanzi', 'frequency_sn', 'frequency_count']]
        missing_df = missing_df.sort_values('frequency_sn')
        
        print("\nMissing hanzi characters with their frequency information:")
        print(missing_df.to_string(index=False))
        
        # Save missing hanzi to a CSV file
        output_file = 'other/missing_hanzi_in_pinyin_v7_with_sn_updated.csv'
        missing_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nMissing hanzi have been saved to {output_file}")

if __name__ == "__main__":
    check_hanzi_existence() 