import csv
from collections import defaultdict

def validate_pinyin_hanzi_length():
    mismatches = defaultdict(list)
    total_rows = 0
    mismatch_count = 0
    
    with open('raw_data/xdhy_rest_hanzi_pinyin_v1_spaced.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row_num, row in enumerate(reader, start=1):
            total_rows += 1
            hanzi = row['hanzi']
            pinyin = row['pinyin']
            
            # Count pinyin syllables (split by space)
            pinyin_syllables = len(pinyin.split())
            hanzi_length = len(hanzi)
            
            if pinyin_syllables != hanzi_length:
                mismatch_count += 1
                mismatches[f"Line {row_num}"].append({
                    'hanzi': hanzi,
                    'pinyin': pinyin,
                    'hanzi_length': hanzi_length,
                    'pinyin_syllables': pinyin_syllables
                })
    
    # Print summary
    print(f"\nValidation Summary:")
    print(f"Total rows checked: {total_rows}")
    print(f"Rows with mismatches: {mismatch_count}")
    print(f"Percentage of mismatches: {(mismatch_count/total_rows)*100:.2f}%")
    
    # Print detailed mismatch information
    if mismatches:
        print("\nDetailed Mismatch Information:")
        for line_num, entries in mismatches.items():
            for entry in entries:
                print(f"\n{line_num}:")
                print(f"Hanzi: {entry['hanzi']} (length: {entry['hanzi_length']})")
                print(f"Pinyin: {entry['pinyin']} (syllables: {entry['pinyin_syllables']})")

if __name__ == "__main__":
    validate_pinyin_hanzi_length()