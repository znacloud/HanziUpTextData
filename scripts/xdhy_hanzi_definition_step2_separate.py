#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to separate definition entries based on whether they correspond to 
single hanzi or multi-character entries (cihui).
Uses the pinyin file to determine hanzi length for each pinyin_id.
"""

import csv
import os
from pathlib import Path

def create_pinyin_id_mappings():
    """
    Create mappings from pinyin_id to category using the already separated pinyin files.
    Returns two sets: single_pinyin_ids and cihui_pinyin_ids.
    """
    single_pinyin_file = Path("others/xdhy_core_hanzi_pinyin_v8_single.csv")
    cihui_pinyin_file = Path("others/xdhy_core_hanzi_pinyin_v8_cihui.csv")
    
    if not single_pinyin_file.exists():
        print(f"Error: Single pinyin file {single_pinyin_file} does not exist!")
        return None, None
    
    if not cihui_pinyin_file.exists():
        print(f"Error: Cihui pinyin file {cihui_pinyin_file} does not exist!")
        return None, None
    
    single_pinyin_ids = set()
    cihui_pinyin_ids = set()
    
    try:
        # Read single hanzi pinyin_ids
        with open(single_pinyin_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                print("Error: Could not read fieldnames from single pinyin CSV file!")
                return None, None
            
            for row in reader:
                pinyin_id = row['pinyin_id']
                single_pinyin_ids.add(pinyin_id)
        
        # Read cihui pinyin_ids
        with open(cihui_pinyin_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                print("Error: Could not read fieldnames from cihui pinyin CSV file!")
                return None, None
            
            for row in reader:
                pinyin_id = row['pinyin_id']
                cihui_pinyin_ids.add(pinyin_id)
        
        print(f"Created mappings: {len(single_pinyin_ids)} single pinyin_ids, {len(cihui_pinyin_ids)} cihui pinyin_ids")
        return single_pinyin_ids, cihui_pinyin_ids
        
    except Exception as e:
        print(f"Error reading pinyin files: {e}")
        return None, None

def separate_definitions_by_hanzi_length():
    """
    Separate definition entries based on the length of the corresponding hanzi.
    Single character definitions go to single.csv
    Multi-character definitions go to cihui.csv
    """
    
    # Input and output file paths
    input_file = Path("others/xdhy_core_hanzi_definition_v7_with_pos.csv")
    single_output_file = Path("others/xdhy_core_hanzi_definition_v8_single.csv")
    cihui_output_file = Path("others/xdhy_core_hanzi_definition_v8_cihui.csv")
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file {input_file} does not exist!")
        return
    
    # Create mappings from pinyin_id to category
    single_pinyin_ids, cihui_pinyin_ids = create_pinyin_id_mappings()
    if single_pinyin_ids is None or cihui_pinyin_ids is None:
        return
    
    # Counters for statistics
    single_count = 0
    cihui_count = 0
    total_count = 0
    missing_pinyin_id_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(single_output_file, 'w', encoding='utf-8', newline='') as single_outfile, \
             open(cihui_output_file, 'w', encoding='utf-8', newline='') as cihui_outfile:
            
            # Create CSV readers and writers
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                print("Error: Could not read fieldnames from definition CSV file!")
                return
                
            single_writer = csv.DictWriter(single_outfile, fieldnames=fieldnames)
            cihui_writer = csv.DictWriter(cihui_outfile, fieldnames=fieldnames)
            
            # Write headers to both output files
            single_writer.writeheader()
            cihui_writer.writeheader()
            
            # Process each row
            for row in reader:
                total_count += 1
                pinyin_id = row['pinyin_id']
                
                # Check if we have the pinyin_id in our mappings
                if pinyin_id in single_pinyin_ids:
                    # Single character - write to single file
                    single_writer.writerow(row)
                    single_count += 1
                elif pinyin_id in cihui_pinyin_ids:
                    # Multi-character - write to cihui file
                    cihui_writer.writerow(row)
                    cihui_count += 1
                else:
                    # Missing pinyin_id in mapping - skip this row
                    missing_pinyin_id_count += 1
                    print(f"Warning: pinyin_id {pinyin_id} not found in pinyin mappings")
                
                # Print progress every 1000 rows
                if total_count % 1000 == 0:
                    print(f"Processed {total_count} rows...")
        
        # Print final statistics
        print(f"\nSeparation completed successfully!")
        print(f"Total rows processed: {total_count}")
        print(f"Single hanzi definitions: {single_count} -> {single_output_file}")
        print(f"Multi-character definitions: {cihui_count} -> {cihui_output_file}")
        print(f"Missing pinyin_id references: {missing_pinyin_id_count}")
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return

if __name__ == "__main__":
    print("Starting definition separation process...")
    separate_definitions_by_hanzi_length()
    print("Process completed.") 