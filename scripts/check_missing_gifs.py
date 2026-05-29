import csv
import os
from pathlib import Path

def main():
    # Paths
    csv_file = './database_csv/jjhy_core_hanzi_pinyin.csv'
    gif_dir = './strokeorder_gifs'
    output_file = './missing_gifs.csv'
    existing_file = './hanzi_gifs.csv'
    
    # Read all hanzi from CSV and split into individual characters
    unique_hanzi = set()
    
    print(f"Reading hanzi from {csv_file}...")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hanzi = row['hanzi']
            # Split multi-character hanzi into individual characters
            for char in hanzi:
                unique_hanzi.add(char)
    
    print(f"Found {len(unique_hanzi)} unique single hanzi characters")
    
    # Check which hanzi are missing gif files and which exist
    missing_hanzi = []
    existing_hanzi = []
    
    print(f"Checking for gif files in {gif_dir}...")
    for hanzi in sorted(unique_hanzi):
        # Get Unicode codepoint for the hanzi
        codepoint = ord(hanzi)
        gif_filename = f"{codepoint}.gif"
        gif_path = os.path.join(gif_dir, gif_filename)
        
        # Check if gif file exists
        if not os.path.exists(gif_path):
            missing_hanzi.append({
                'hanzi': hanzi,
                'unicode_codepoint': codepoint,
                'expected_filename': gif_filename
            })
        else:
            existing_hanzi.append({
                'hanzi': hanzi,
                'unicode_codepoint': codepoint,
                'gif_filename': gif_filename
            })
    
    print(f"Found {len(missing_hanzi)} hanzi without gif files")
    print(f"Found {len(existing_hanzi)} hanzi with gif files")
    
    # Save missing hanzi to CSV
    if missing_hanzi:
        print(f"Saving missing hanzi to {output_file}...")
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['hanzi', 'unicode_codepoint', 'expected_filename']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(missing_hanzi)
    
    # Save existing hanzi to CSV
    if existing_hanzi:
        print(f"Saving existing hanzi to {existing_file}...")
        with open(existing_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['hanzi', 'unicode_codepoint', 'gif_filename']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_hanzi)
    
    print(f"\nSummary:")
    print(f"  Total unique hanzi: {len(unique_hanzi)}")
    print(f"  With gif files: {len(existing_hanzi)}")
    print(f"  Missing gif files: {len(missing_hanzi)}")
    if missing_hanzi:
        print(f"  Missing hanzi saved to: {output_file}")
    if existing_hanzi:
        print(f"  Existing hanzi saved to: {existing_file}")
    
    # Show first few missing hanzi
    if len(missing_hanzi) > 0:
        print(f"\nFirst 10 missing hanzi:")
        for item in missing_hanzi[:10]:
            print(f"  {item['hanzi']} (U+{item['unicode_codepoint']:04X}, {item['expected_filename']})")

if __name__ == '__main__':
    main()
