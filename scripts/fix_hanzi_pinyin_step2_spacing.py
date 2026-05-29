import csv
import argparse
from pinyin_utils import split_pinyin

def get_tone_mark(char):
    # Returns the tone number (1-4) for a character with tone mark, 0 if no tone
    if 'ā' in char or 'ē' in char or 'ī' in char or 'ō' in char or 'ū' in char or 'ǖ' in char:
        return 1
    if 'á' in char or 'é' in char or 'í' in char or 'ó' in char or 'ú' in char or 'ǘ' in char:
        return 2
    if 'ǎ' in char or 'ě' in char or 'ǐ' in char or 'ǒ' in char or 'ǔ' in char or 'ǚ' in char:
        return 3
    if 'à' in char or 'è' in char or 'ì' in char or 'ò' in char or 'ù' in char or 'ǜ' in char:
        return 4
    return 0

def separate_pinyin_syllables(pinyin):
    # Special cases that should be treated as single syllables
    special_syllables = {'er', 'zi', 'zhi', 'chi', 'shi', 'ri'}
    
    # If it's a special syllable, return as is
    if pinyin in special_syllables:
        return pinyin
    
    # Define consonants and vowels
    consonants = 'bpmfdtnlgkhjqxrzcsyw'
    vowels = 'aāáǎàeēéěèiīíǐìoōóǒòuūúǔùüǖǘǚǜ'
    valid_endings = vowels + 'nngr'
    
    # If the pinyin is short (2 chars or less), return as is
    if len(pinyin) <= 2:
        return pinyin
    
    # Find all possible split points
    split_points = []
    i = 1
    while i < len(pinyin)-1:
        # Check if current position is a valid split point
        # Current char should be a vowel or valid ending
        # Next char should be a consonant
        if pinyin[i] in valid_endings and pinyin[i+1] in consonants:
            # Special handling for n/ng endings
            if pinyin[i] == 'n':
                # If next char is 'g', don't split here (it's part of 'ng')
                if pinyin[i+1] == 'g':
                    i += 1
                    continue
                # If we're at a vowel + n, this is the end of the first syllable
                if pinyin[i-1] in vowels:
                    split_points.append(i+1)
                    i += 1
                    continue
            # If next char is 'n' and the one after is 'g', don't split here
            if pinyin[i+1] == 'n' and i+2 < len(pinyin) and pinyin[i+2] == 'g':
                i += 1
                continue
            split_points.append(i+1)
        i += 1
    
    # If no valid split points found, return as is
    if not split_points:
        return pinyin
    
    # Split the pinyin at the first valid point
    return pinyin[:split_points[0]] + ' ' + pinyin[split_points[0]:]

def fix_pinyin_spacing(input_file, output_file):
    # Read the original CSV
    rows = []
    multiple_splits_count = 0
    no_valid_count = 0
    no_split_count = 0
    success_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ['status']
        line_count = 0
        for row in reader:
            line_count += 1
            original_pinyin = row['pinyin'].strip()
            if original_pinyin:
                # Use our new pinyin splitting algorithm with hanzi context
                new_pinyin, status = split_pinyin(line_count,original_pinyin, row['hanzi'])
                if status == "success":
                    success_count += 1
                elif status == "multiple_valid":
                    multiple_splits_count += 1
                elif status == "no_valid":
                    no_valid_count += 1
                elif status == "no_split":
                    no_split_count += 1
                row['pinyin'] = new_pinyin
                row['status'] = status
                rows.append(row)
    
    # sort rows by status
    rows.sort(key=lambda x: x['status'])
    
    # Write the updated CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total rows processed: {len(rows)}")
    print(f"Entries that were multiple valid splits: {multiple_splits_count}")
    print(f"Entries that were not split: {no_split_count}")
    print(f"Entries that were not valid: {no_valid_count}")
    print(f"Entries that were successful: {success_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fix pinyin spacing in a CSV file.')
    parser.add_argument('input_file', help='Path to the input CSV file')
    parser.add_argument('output_file', help='Path to the output CSV file')
    parser.add_argument('--default', action='store_true', 
                       help='Use default paths (database_csv/hanzi_pinyin_v1.csv and database_csv/hanzi_pinyin_v2.csv)')
    
    args = parser.parse_args()
    
    if args.default:
        input_file = 'database_csv/hanzi_pinyin_v1.csv'
        output_file = 'database_csv/hanzi_pinyin_v2.csv'
    else:
        input_file = args.input_file
        output_file = args.output_file
    
    fix_pinyin_spacing(input_file, output_file) 