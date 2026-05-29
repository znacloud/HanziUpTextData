#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to separate example entries based on whether they correspond to 
single hanzi or multi-character entries (cihui).
Uses the definition file to map definition_id to pinyin_id, then uses
the already separated pinyin files to determine the category.
"""

import csv
import os
from pathlib import Path

def create_definition_id_mappings():
    """
    Create mappings from definition_id to category using the already separated definition files.
    Returns two sets: single_definition_ids and cihui_definition_ids.
    """
    single_definition_file = Path("others/xdhy_core_hanzi_definition_v8_single.csv")
    cihui_definition_file = Path("others/xdhy_core_hanzi_definition_v8_cihui.csv")
    
    if not single_definition_file.exists():
        print(f"Error: Single definition file {single_definition_file} does not exist!")
        return None, None
    
    if not cihui_definition_file.exists():
        print(f"Error: Cihui definition file {cihui_definition_file} does not exist!")
        return None, None
    
    single_definition_ids = set()
    cihui_definition_ids = set()
    
    try:
        # Read single hanzi definition_ids
        with open(single_definition_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                print("Error: Could not read fieldnames from single definition CSV file!")
                return None, None
            
            for row in reader:
                definition_id = row['definition_id']
                single_definition_ids.add(definition_id)
        
        # Read cihui definition_ids
        with open(cihui_definition_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                print("Error: Could not read fieldnames from cihui definition CSV file!")
                return None, None
            
            for row in reader:
                definition_id = row['definition_id']
                cihui_definition_ids.add(definition_id)
        
        print(f"Created mappings: {len(single_definition_ids)} single definition_ids, {len(cihui_definition_ids)} cihui definition_ids")
        return single_definition_ids, cihui_definition_ids
        
    except Exception as e:
        print(f"Error reading definition files: {e}")
        return None, None

def separate_examples_by_hanzi_length():
    """
    Separate example entries based on the length of the corresponding hanzi.
    Single character examples go to single.csv
    Multi-character examples go to cihui.csv
    """
    
    # Input and output file paths
    input_file = Path("raw_data/xdhy_core_hanzi_example.csv")
    single_output_file = Path("others/xdhy_core_hanzi_example_v8_single.csv")
    cihui_output_file = Path("others/xdhy_core_hanzi_example_v8_cihui.csv")
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file {input_file} does not exist!")
        return
    
    # Create mappings from definition_id to category
    single_definition_ids, cihui_definition_ids = create_definition_id_mappings()
    if single_definition_ids is None or cihui_definition_ids is None:
        return
    
    # Counters for statistics
    single_count = 0
    cihui_count = 0
    total_count = 0
    missing_definition_id_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(single_output_file, 'w', encoding='utf-8', newline='') as single_outfile, \
             open(cihui_output_file, 'w', encoding='utf-8', newline='') as cihui_outfile:
            
            # Create CSV readers and writers
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                print("Error: Could not read fieldnames from example CSV file!")
                return
                
            single_writer = csv.DictWriter(single_outfile, fieldnames=fieldnames)
            cihui_writer = csv.DictWriter(cihui_outfile, fieldnames=fieldnames)
            
            # Write headers to both output files
            single_writer.writeheader()
            cihui_writer.writeheader()
            
            # Process each row
            for row in reader:
                total_count += 1
                definition_id = row['definition_id']
                
                # Check if we have the definition_id in our mappings
                if definition_id in single_definition_ids:
                    # Single character - write to single file
                    single_writer.writerow(row)
                    single_count += 1
                elif definition_id in cihui_definition_ids:
                    # Multi-character - write to cihui file
                    cihui_writer.writerow(row)
                    cihui_count += 1
                else:
                    # Missing definition_id in mapping - skip this row
                    missing_definition_id_count += 1
                    print(f"Warning: definition_id {definition_id} not found in definition mappings")
                
                # Print progress every 1000 rows
                if total_count % 1000 == 0:
                    print(f"Processed {total_count} rows...")
        
        # Print final statistics
        print(f"\nSeparation completed successfully!")
        print(f"Total rows processed: {total_count}")
        print(f"Single hanzi examples: {single_count} -> {single_output_file}")
        print(f"Multi-character examples: {cihui_count} -> {cihui_output_file}")
        print(f"Missing definition_id references: {missing_definition_id_count}")
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return

if __name__ == "__main__":
    print("Starting example separation process...")
    separate_examples_by_hanzi_length()
    print("Process completed.") 