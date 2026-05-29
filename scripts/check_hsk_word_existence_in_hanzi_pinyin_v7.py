import pandas as pd
from pathlib import Path

def check_hsk_entries():
    # Read the CSV files
    hsk_df = pd.read_csv('database_csv/hsk_word.csv')
    hanzi_pinyin_df = pd.read_csv('database_csv/hanzi_pinyin_v7_with_sn_updated.csv')
    
    # Create a set of tuples (hanzi, pinyin) from hanzi_pinyin_v2.csv for faster lookup
    hanzi_pinyin_set = set(zip(hanzi_pinyin_df['hanzi'], hanzi_pinyin_df['pinyin'].str.lower()))
    
    # Initialize counters and lists
    found_entries = []
    missing_entries = []
    
    # Check each entry in hsk_word.csv
    for _, row in hsk_df.iterrows():
        entry = (row['hanzi'], row['pinyin'].lower())
        if entry in hanzi_pinyin_set:
            found_entries.append(entry)
        else:
            missing_entries.append((row['hsk_sn'], row['hanzi'], row['pinyin'], row['hsk_level']))
    
    # Print results
    total_entries = len(hsk_df)
    print(f"\nResults of checking {total_entries} HSK entries:")
    print(f"Found: {len(found_entries)} entries")
    print(f"Missing: {len(missing_entries)} entries")
    
    if missing_entries:
        print("\nMissing entries:")
        for _, hanzi, pinyin, _ in missing_entries:
            print(f"Hanzi: {hanzi}, Pinyin: {pinyin}")
    
    # Save missing entries to a CSV file
    if missing_entries:
        missing_df = pd.DataFrame(missing_entries, columns=['hsk_sn', 'hanzi', 'pinyin', 'hsk_level'])
        missing_df.to_csv('other/missing_hsk_words_in_pinyin_v7_with_sn_updated.csv', index=False)
        print("\nMissing entries have been saved to 'other/missing_definitions_hsk_entries.csv'")

if __name__ == "__main__":
    check_hsk_entries() 