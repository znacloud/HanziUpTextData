#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to separate hanzi entries based on their length.
Single hanzi characters are saved to xdhy_core_hanzi_pinyin_v8_single.csv
Multi-character entries are saved to xdhy_core_hanzi_pinyin_v8_cihui.csv
"""

import csv
import os
from pathlib import Path

def separate_hanzi_by_length():
    """
    Separate hanzi entries based on the length of the hanzi field.
    Single characters (length = 1) go to single.csv
    Multi-character entries (length > 1) go to cihui.csv
    """
    
    # Input and output file paths
    input_file = Path("others/xdhy_core_hanzi_pinyin_v7_latest.csv")
    single_output_file = Path("others/xdhy_core_hanzi_pinyin_v8_single.csv")
    cihui_output_file = Path("others/xdhy_core_hanzi_pinyin_v8_cihui.csv")
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file {input_file} does not exist!")
        return
    
    # Counters for statistics
    single_count = 0
    cihui_count = 0
    total_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(single_output_file, 'w', encoding='utf-8', newline='') as single_outfile, \
             open(cihui_output_file, 'w', encoding='utf-8', newline='') as cihui_outfile:
            
            # Create CSV readers and writers
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                print("Error: Could not read fieldnames from CSV file!")
                return
            single_writer = csv.DictWriter(single_outfile, fieldnames=fieldnames)
            cihui_writer = csv.DictWriter(cihui_outfile, fieldnames=fieldnames)
            
            # Write headers to both output files
            single_writer.writeheader()
            cihui_writer.writeheader()
            
            # Process each row
            for row in reader:
                total_count += 1
                hanzi = row['hanzi']
                
                # Check the length of the hanzi field
                if len(hanzi) == 1:
                    # Single character - write to single file
                    single_writer.writerow(row)
                    single_count += 1
                else:
                    # Multi-character - write to cihui file
                    cihui_writer.writerow(row)
                    cihui_count += 1
                
                # Print progress every 1000 rows
                if total_count % 1000 == 0:
                    print(f"Processed {total_count} rows...")
        
        # Print final statistics
        print(f"\nSeparation completed successfully!")
        print(f"Total rows processed: {total_count}")
        print(f"Single hanzi entries: {single_count} -> {single_output_file}")
        print(f"Multi-character entries: {cihui_count} -> {cihui_output_file}")
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return

if __name__ == "__main__":
    print("Starting hanzi separation process...")
    separate_hanzi_by_length()
    print("Process completed.")