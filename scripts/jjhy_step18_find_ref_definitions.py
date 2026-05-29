#!/usr/bin/env python3
"""
Script to find corresponding definitions for ref_cihui and ref_sn from refdefinition files.
This script processes files with pattern "jjhy_csv/refdefinition/jjhy_.*_ref_\d+.csv"
and looks up definitions in ALL files in "jjhy_csv/final_merged/".
"""

import os
import re
import pandas as pd
import glob
from pathlib import Path
import argparse

def find_refdefinition_files():
    """Find all refdefinition files matching the pattern."""
    pattern = "jjhy_csv/refdefinition/jjhy_*_ref_*.csv"
    files = glob.glob(pattern)
    return [f for f in files if os.path.isfile(f)]

def find_all_final_merged_files():
    """Find all final_merged files."""
    pattern = "jjhy_csv/final_merged/jjhy_*_parsed_*_filtered.csv"
    files = glob.glob(pattern)
    return [f for f in files if os.path.isfile(f)]

def parse_ref_sn(ref_sn_str):
    """Parse ref_sn string to extract individual numbers."""
    if not ref_sn_str or pd.isna(ref_sn_str):
        return []
    
    # Handle cases like "①②", "①", "1", "1,2", etc.
    ref_sn_str = str(ref_sn_str)
    
    # Extract numbers from circled numbers or regular numbers
    numbers = []
    
    # Handle circled numbers (①, ②, ③, etc.)
    circled_pattern = r'[①②③④⑤⑥⑦⑧⑨⑩]'
    circled_matches = re.findall(circled_pattern, ref_sn_str)
    for match in circled_matches:
        # Convert circled numbers to regular numbers
        circled_to_num = {
            '①': 1, '②': 2, '③': 3, '④': 4, '⑤': 5,
            '⑥': 6, '⑦': 7, '⑧': 8, '⑨': 9, '⑩': 10
        }
        numbers.append(circled_to_num.get(match, 0))
    
    # Handle regular numbers
    num_pattern = r'\d+'
    num_matches = re.findall(num_pattern, ref_sn_str)
    for match in num_matches:
        numbers.append(int(match))
    
    return numbers if numbers else [1]  # Default to 1 if no numbers found

def find_definitions_in_file(ref_cihui, ref_sn, final_df, search_field, match_type_prefix):
    """Find definitions for a specific ref_cihui and ref_sn in a single final_merged file."""
    matching_rows = final_df[
        (final_df[search_field] == ref_cihui) & 
        (final_df['sn'] == ref_sn)
    ]
    
    results = []
    if not matching_rows.empty:
        for _, match_row in matching_rows.iterrows():
            result = {
                'matched_value': match_row.get(search_field, ''),
                'matched_sn': match_row.get('sn', ''),
                'definition': match_row.get('definition', '')
            }
            results.append(result)
    
    return results

def find_definitions(ref_file_path, output_file=None):
    """Find definitions for ref_cihui and ref_sn combinations across all final_merged files."""
    
    print(f"Processing: {ref_file_path}")
    
    # Read refdefinition file
    try:
        ref_df = pd.read_csv(ref_file_path)
        print(f"Found {len(ref_df)} rows in refdefinition file")
    except Exception as e:
        print(f"Error reading refdefinition file: {e}")
        return
    
    # Get all final_merged files
    final_files = find_all_final_merged_files()
    print(f"Found {len(final_files)} final_merged files to search")
    
    # Determine column names based on file type
    if 'hanzi' in ref_file_path:
        ref_cihui_col = 'ref_cihui'
        ref_sn_col = 'ref_sn'
        cihui_col = 'hanzi'  # In hanzi files, the main column is 'hanzi'
    else:
        ref_cihui_col = 'ref_cihui'
        ref_sn_col = 'ref_sn'
        cihui_col = 'cihui'  # In cihui files, the main column is 'cihui'
    
    # Check if required columns exist
    required_cols = [ref_cihui_col, ref_sn_col, cihui_col]
    missing_cols = [col for col in required_cols if col not in ref_df.columns]
    if missing_cols:
        print(f"Missing columns in refdefinition file: {missing_cols}")
        return
    
    # Prepare results
    results = []
    
    for idx, row in ref_df.iterrows():
        ref_cihui = row[ref_cihui_col]
        ref_sn_str = row[ref_sn_col]
        main_item = row[cihui_col]
        
        if pd.isna(ref_cihui) or pd.isna(ref_sn_str):
            continue
        
        # Parse ref_sn to get individual numbers
        ref_sn_numbers = parse_ref_sn(ref_sn_str)
        
        for ref_sn in ref_sn_numbers:
            found_match = False
            
            # Search across all final_merged files
            for final_file in final_files:
                try:
                    # Read the final_merged file
                    final_df = pd.read_csv(final_file)
                    
                    # Determine which field to search in based on the filename
                    filename = os.path.basename(final_file)
                    if 'cihui' in filename:
                        search_field = 'cihui'
                        match_type_prefix = 'cihui'
                    elif 'hanzi' in filename:
                        search_field = 'hanzi'
                        match_type_prefix = 'hanzi'
                    else:
                        continue  # Skip files that don't match our pattern
                    
                    # Check if search field exists
                    if search_field not in final_df.columns:
                        continue
                    
                    # Search for matches in this file
                    file_results = find_definitions_in_file(
                        ref_cihui, ref_sn, final_df, search_field, match_type_prefix
                    )
                    
                    if file_results:
                        found_match = True
                        for file_result in file_results:
                            result = {
                                'main_item': main_item,
                                'ref_cihui': ref_cihui,
                                'ref_sn': ref_sn,
                                'ref_sn_original': ref_sn_str,
                            
                                **file_result
                            }
                            results.append(result)
                        
                        # If we found a match, we can stop searching other files for this ref_cihui/ref_sn
                        break
                        
                except Exception as e:
                    print(f"Error processing {final_file}: {e}")
                    continue
            
            # If no match found in any file
            if not found_match:
                result = {
                    'main_item': main_item,
                    'ref_cihui': ref_cihui,
                    'ref_sn': ref_sn,
                    'ref_sn_original': ref_sn_str,
                    'matched_value': '',
                    'matched_sn': '',
                    'definition': 'NOT_FOUND'
                }
                results.append(result)
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results
    if output_file:
        results_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Results saved to: {output_file}")
    
    # Print summary
    found_count = len(results_df[results_df['definition'] != 'NOT_FOUND'])
    total_count = len(results_df)
    print(f"Found {found_count}/{total_count} definitions")
    
    # Print match type summary
    if 'match_type' in results_df.columns:
        exact_cihui = len(results_df[results_df['match_type'] == 'exact_cihui'])
        exact_hanzi = len(results_df[results_df['match_type'] == 'exact_hanzi'])
        not_found = len(results_df[results_df['match_type'] == 'not_found'])
        
        print(f"  - Exact matches in cihui: {exact_cihui}")
        print(f"  - Exact matches in hanzi: {exact_hanzi}")
        print(f"  - Not found: {not_found}")
    
    return results_df

def main():
    parser = argparse.ArgumentParser(description='Find definitions for ref_cihui and ref_sn')
    parser.add_argument('--output-dir', default='jjhy_csv/ref_definitions_output',
                       help='Output directory for results')
    parser.add_argument('--single-file', help='Process only this specific refdefinition file')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.single_file:
        # Process single file
        if not os.path.exists(args.single_file):
            print(f"File not found: {args.single_file}")
            return
        
        output_file = os.path.join(args.output_dir, 
                                  f"definitions_{os.path.basename(args.single_file)}")
        find_definitions(args.single_file, output_file)
    else:
        # Process all refdefinition files
        ref_files = find_refdefinition_files()
        print(f"Found {len(ref_files)} refdefinition files")
        
        all_results = []
        
        for ref_file in ref_files:
            output_file = os.path.join(args.output_dir, 
                                      f"definitions_{os.path.basename(ref_file)}")
            
            result_df = find_definitions(ref_file, output_file)
            if result_df is not None:
                all_results.append(result_df)
        
        # Combine all results
        if all_results:
            combined_df = pd.concat(all_results, ignore_index=True)
            combined_output = os.path.join(args.output_dir, 'all_definitions_combined.csv')
            combined_df.to_csv(combined_output, index=False, encoding='utf-8')
            print(f"Combined results saved to: {combined_output}")
            
            # Print overall summary
            total_found = len(combined_df[combined_df['definition'] != 'NOT_FOUND'])
            total_count = len(combined_df)
            print(f"\nOverall summary: Found {total_found}/{total_count} definitions")

if __name__ == "__main__":
    main()
