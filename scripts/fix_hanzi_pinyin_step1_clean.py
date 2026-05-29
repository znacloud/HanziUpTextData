import csv
import re
import argparse
    # Valid pinyin characters: a-z, ü, and tone marks
    # Tone marks: āáǎà, ēéěè, īíǐì, ōóǒò, ūúǔù, ǖǘǚǜ
valid_chars = set('abcdefghijklmnopqrstuvwxyzü ')
tone_marks = set('āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ')

def is_valid_pinyin(pinyin):

    
    # Check if all characters are either valid base characters or tone marks
    return all(c.lower() in valid_chars or c in tone_marks for c in pinyin)

def clean_pinyin(pinyin):
    # Remove the "∥·" prefix if present
    pinyin = pinyin.replace('∥·', '')
    
    # Replace 'ɑ' with 'a'
    pinyin = pinyin.replace('ɑ', 'a')
    
    # Convert to lowercase (but preserve tone marks)
    pinyin = pinyin.lower()
    
    # Replace invalid characters with space
    cleaned = ''
    for char in pinyin:
        if char.lower() in valid_chars or char in tone_marks:
            cleaned += char
        else:
            cleaned += ' '
    
    # Remove multiple spaces and trim
    cleaned = ' '.join(cleaned.split())
    
    return cleaned

def check_and_correct_pinyin(input_file, output_file):
    # Read the original CSV
    rows = []
    issues = []
    corrections = []
    
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames #+ ['is_valid', 'original_pinyin']
        
        for row in reader:
            original_pinyin = row['pinyin']
            cleaned_pinyin = clean_pinyin(original_pinyin)
            is_valid = is_valid_pinyin(cleaned_pinyin)
            
            # Store the original pinyin and validation status
            # row['original_pinyin'] = original_pinyin
            # row['is_valid'] = '1' if is_valid else '0'
            
            # If the pinyin was modified, store the correction
            if cleaned_pinyin != original_pinyin:
                row['pinyin'] = cleaned_pinyin
                corrections.append({
                    'pinyin_id': row['pinyin_id'],
                    'hanzi': row['hanzi'],
                    'original': original_pinyin,
                    'corrected': cleaned_pinyin
                })
            
            # If the pinyin is still invalid after cleaning, add to issues
            if not is_valid:
                issues.append({
                    'pinyin_id': row['pinyin_id'],
                    'hanzi': row['hanzi'],
                    'pinyin': cleaned_pinyin
                })
            
            rows.append(row)
    
    # Write the updated CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    
    if corrections:
        print("\nCorrections made:")
        print("-" * 80)
        for corr in corrections:
            print(f"ID: {corr['pinyin_id']}, Hanzi: {corr['hanzi']}")
            print(f"Original: {corr['original']} -> Corrected: {corr['corrected']}")
            print("-" * 80)
    
    if issues:
        print("\nRemaining issues (needs manual review):")
        print("-" * 80)
        for issue in issues:
            print(f"ID: {issue['pinyin_id']}, Hanzi: {issue['hanzi']}, Pinyin: {issue['pinyin']}")
            print("-" * 80)

    # Print summary
    print(f"\nSummary:")
    print(f"Total rows processed: {len(rows)}")
    print(f"Rows with corrections: {len(corrections)}")
    print(f"Rows with remaining issues: {len(issues)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clean and validate pinyin data from a CSV file.')
    parser.add_argument('input_file', help='Path to the input CSV file')
    parser.add_argument('output_file', help='Path to the output CSV file')
    parser.add_argument('--default', action='store_true', 
                       help='Use default paths (database_csv/hanzi_pinyin.csv and database_csv/hanzi_pinyin_v1.csv)')
    
    args = parser.parse_args()
    
    if args.default:
        input_file = 'database_csv/hanzi_pinyin.csv'
        output_file = 'database_csv/hanzi_pinyin_v1.csv'
    else:
        input_file = args.input_file
        output_file = args.output_file
    
    check_and_correct_pinyin(input_file, output_file) 