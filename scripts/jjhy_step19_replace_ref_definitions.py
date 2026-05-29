#!/usr/bin/env python3
"""
Script to replace reference symbols in parsed definition files with their mapped definitions.
This script processes files with pattern "jjhy_csv/refdefinition/jjhy_.*_parsed_\d+_filtered.csv"
and replaces references like "组①" with "【组】把分散的人或事物结合成为一个整体或系统".
"""

import os
import re
import pandas as pd
import glob
from pathlib import Path
import argparse

def find_parsed_files():
    """Find all parsed files matching the pattern."""
    pattern = "jjhy_csv/refdefinition/jjhy_*_parsed_*_filtered.csv"
    files = glob.glob(pattern)
    return [f for f in files if os.path.isfile(f)]

def get_corresponding_mapped_definitions_file(parsed_file_path):
    """Get the corresponding mapped definitions file path."""
    # Extract the base name and type from parsed file path
    # e.g., jjhy_csv/refdefinition/jjhy_cihui_parsed_5000_filtered.csv
    # -> jjhy_csv/ref_definitions_output/definitions_jjhy_cihui_ref_5000.csv
    
    filename = os.path.basename(parsed_file_path)
    
    # Extract type (cihui or hanzi) and number
    match = re.match(r'jjhy_(cihui|hanzi)_parsed_(\d+)_filtered\.csv', filename)
    if not match:
        return None
    
    file_type, number = match.groups()
    
    # Construct the corresponding mapped definitions file path
    mapped_file = f"jjhy_csv/ref_definitions_output/definitions_jjhy_{file_type}_ref_{number}.csv"
    
    return mapped_file if os.path.exists(mapped_file) else None

def process_parsed_file(parsed_file_path, output_dir):
    """Process a single parsed file and replace references with mapped definitions."""
    
    print(f"Processing: {parsed_file_path}")
    
    # Read the parsed file
    try:
        parsed_df = pd.read_csv(parsed_file_path)
        print(f"Found {len(parsed_df)} rows in parsed file")
    except Exception as e:
        print(f"Error reading parsed file: {e}")
        return None
    
    # Get the corresponding mapped definitions file
    mapped_file = get_corresponding_mapped_definitions_file(parsed_file_path)
    if not mapped_file:
        print(f"No corresponding mapped definitions file found for: {parsed_file_path}")
        return None
    
    # Read the mapped definitions file
    try:
        mapped_df = pd.read_csv(mapped_file)
        print(f"Found {len(mapped_df)} mapped definitions")
    except Exception as e:
        print(f"Error reading mapped definitions file: {e}")
        return None
    
    # Create a copy of the parsed dataframe
    result_df = parsed_df.copy()
    
    # Process each row
    replacements_made = 0
    
    for idx, row in result_df.iterrows():
        definition = row['definition']
        if pd.isna(definition):
            continue
        
        # Get the main item (cihui or hanzi) for this row
        main_item = row.get('cihui') or row.get('hanzi')
        if pd.isna(main_item):
            continue
        
        # Find all mapped definitions for this main_item
        item_definitions = mapped_df[mapped_df['main_item'] == main_item]
        
        if item_definitions.empty:
            continue
        
        # For each mapped definition, try to replace references
        for _, mapped_row in item_definitions.iterrows():
            ref_cihui = mapped_row['ref_cihui']
            ref_sn_original = mapped_row['ref_sn_original']
            mapped_definition = mapped_row['definition']
            
            if pd.isna(ref_cihui) or pd.isna(ref_sn_original) or mapped_definition == 'NOT_FOUND':
                continue
            
            # Convert to strings to avoid re.escape() errors
            ref_cihui = str(ref_cihui)
            ref_sn_original = str(ref_sn_original)
            
            # Convert ref_sn_original to both regular number and circled number for matching
            # ref_sn_original contains regular numbers (1, 2, 3) but text has circled numbers (①, ②, ③)
            circled_to_num = {
                '①': '1', '②': '2', '③': '3', '④': '4', '⑤': '5',
                '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9', '⑩': '10'
            }
            
            # Try to find the circled number that corresponds to ref_sn_original
            circled_sn = None
            for circled, num in circled_to_num.items():
                if num == ref_sn_original:
                    circled_sn = circled
                    break
            
            # Create patterns to find and replace
            patterns_to_try = []
            
            # Pattern 1: ref_cihui followed by circled number (most common case)
            if circled_sn:
                patterns_to_try.append(f'["]?({re.escape(ref_cihui)}).*?({re.escape(circled_sn)})["]?')
            
            # Pattern 2: ref_cihui followed by regular number (fallback)
            patterns_to_try.append(f'["]?({re.escape(ref_cihui)}).*?({re.escape(ref_sn_original)})["]?')
            
            # Try each pattern
            replacement_made = False
            for pattern in patterns_to_try:
                # Find matches
                matches = re.findall(pattern, definition)
                if matches:
                    # Replace with the format "【ref_cihui】definition"
                    replacement = f"【{ref_cihui}】{mapped_definition}"
                    
                    # Replace all occurrences
                    definition = re.sub(pattern, replacement, definition)
                    replacements_made += 1
                    replacement_made = True
                    
                    # Debug: print what we're replacing
                    print(f"DEBUG: Replacing '{ref_cihui}{circled_sn or ref_sn_original}' with '{replacement}' in '{main_item}'")
                    break
            
            if not replacement_made:
                # Debug: print what we're looking for but not finding
                print(f"DEBUG: Looking for patterns in definition: '{definition}'")
                for pattern in patterns_to_try:
                    print(f"DEBUG:   Pattern: {pattern}")
        
        # Update the result dataframe
        result_df.at[idx, 'definition'] = definition
    
    print(f"Made {replacements_made} replacements")
    
    # Save the result
    filename = os.path.basename(parsed_file_path)
    output_file = os.path.join(output_dir, filename)
    result_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Saved result to: {output_file}")
    
    return result_df

def main():
    parser = argparse.ArgumentParser(description='Replace reference symbols with mapped definitions')
    parser.add_argument('--output-dir', default='jjhy_csv/ref_definitions_replaced',
                       help='Output directory for results')
    parser.add_argument('--single-file', help='Process only this specific parsed file')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.single_file:
        # Process single file
        if not os.path.exists(args.single_file):
            print(f"File not found: {args.single_file}")
            return
        
        process_parsed_file(args.single_file, args.output_dir)
    else:
        # Process all parsed files
        parsed_files = find_parsed_files()
        print(f"Found {len(parsed_files)} parsed files")
        
        for parsed_file in parsed_files:
            process_parsed_file(parsed_file, args.output_dir)
            print("-" * 50)

if __name__ == "__main__":
    main()
