#!/usr/bin/env python3
"""
Script to enhance duplicated_examples.csv by prepending hanzi and definition
for each definition_id.
"""

import csv
import os
import sys
from pathlib import Path

def load_definitions(definitions_file):
    """Load definitions data into a dictionary keyed by definition_id."""
    definitions = {}
    with open(definitions_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            definition_id = row['definition_id']
            pinyin_id = row['pinyin_id']
            definition_cn = row['definition_cn']
            definitions[definition_id] = {
                'pinyin_id': pinyin_id,
                'definition_cn': definition_cn
            }
    return definitions

def load_pinyin_data(pinyin_file):
    """Load pinyin data into a dictionary keyed by pinyin_id."""
    pinyin_data = {}
    with open(pinyin_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pinyin_id = row['pinyin_id']
            hanzi = row['hanzi']
            pinyin_data[pinyin_id] = hanzi
    return pinyin_data

def enhance_duplicated_examples():
    """Main function to enhance the duplicated_examples.csv file."""
    
    # Define file paths
    base_dir = Path(__file__).parent.parent
    duplicated_file = base_dir / 'others' / 'duplicated_examples.csv'
    definitions_file = base_dir / 'database_csv' / 'hanzi_definition_v7_with_pos_updated.csv'
    pinyin_file = base_dir / 'database_csv' / 'hanzi_pinyin_v7_with_sn_updated.csv'
    output_file = base_dir / 'others' / 'duplicated_examples_enhanced.csv'
    
    # Check if files exist
    if not duplicated_file.exists():
        print(f"Error: {duplicated_file} not found")
        return
    
    if not definitions_file.exists():
        print(f"Error: {definitions_file} not found")
        return
    
    if not pinyin_file.exists():
        print(f"Error: {pinyin_file} not found")
        return
    
    print("Loading definitions data...")
    definitions = load_definitions(definitions_file)
    print(f"Loaded {len(definitions)} definitions")
    
    print("Loading pinyin data...")
    pinyin_data = load_pinyin_data(pinyin_file)
    print(f"Loaded {len(pinyin_data)} pinyin entries")
    
    # Read and enhance the duplicated examples
    enhanced_rows = []
    missing_definitions = []
    missing_pinyin = []
    
    print("Processing duplicated examples...")
    with open(duplicated_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Create new header with hanzi and definition columns prepended
        new_header = ['hanzi', 'definition_cn'] + list(reader.fieldnames)
        
        for row in reader:
            definition_id = row['definition_id']
            
            # Get definition data
            if definition_id in definitions:
                def_data = definitions[definition_id]
                pinyin_id = def_data['pinyin_id']
                definition_cn = def_data['definition_cn']
                
                # Get hanzi from pinyin data
                if pinyin_id in pinyin_data:
                    hanzi = pinyin_data[pinyin_id]
                else:
                    hanzi = 'N/A'
                    missing_pinyin.append(pinyin_id)
            else:
                hanzi = 'N/A'
                definition_cn = 'N/A'
                missing_definitions.append(definition_id)
            
            # Create enhanced row
            enhanced_row = [hanzi, definition_cn] + [row[field] for field in reader.fieldnames]
            enhanced_rows.append(enhanced_row)
    
    # Write enhanced data to output file
    print(f"Writing enhanced data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(new_header)
        writer.writerows(enhanced_rows)
    
    print(f"Successfully enhanced {len(enhanced_rows)} rows")
    print(f"Output written to: {output_file}")
    
    # Report any missing data
    if missing_definitions:
        print(f"\nWarning: {len(missing_definitions)} definition_ids not found in definitions file:")
        print(f"First 10 missing: {missing_definitions[:10]}")
    
    if missing_pinyin:
        print(f"\nWarning: {len(missing_pinyin)} pinyin_ids not found in pinyin file:")
        print(f"First 10 missing: {missing_pinyin[:10]}")

if __name__ == "__main__":
    enhance_duplicated_examples() 