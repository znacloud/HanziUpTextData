#!/usr/bin/env python3
"""
Script to filter out only those rows from parsed files that contain references to multiple-pinyin ref_cihui.
This creates a focused dataset of just the problematic rows.
"""

import os
import glob
import pandas as pd
from collections import defaultdict

def load_multiple_pinyin_ref_cihui():
    """Load the list of ref_cihui that have multiple pinyin pronunciations."""
    try:
        df = pd.read_csv("jjhy_csv/ref_cihui_multiple_pinyin_analysis.csv")
        return set(df['ref_cihui'].tolist())
    except FileNotFoundError:
        print("Error: ref_cihui_multiple_pinyin_analysis.csv not found.")
        print("Please run identify_multiple_pinyin.py first.")
        return set()

def find_parsed_files():
    """Find all parsed CSV files in refdefinition directory."""
    pattern = "jjhy_csv/refdefinition/jjhy_*_parsed_*_filtered.csv"
    files = glob.glob(pattern)
    return sorted(files)

def filter_multiple_pinyin_rows(multiple_pinyin_set):
    """Filter parsed files to extract only rows that reference multiple-pinyin ref_cihui."""
    
    # Dictionary to store filtered rows for each file
    # Format: {filename: [filtered_rows]}
    filtered_data = defaultdict(list)
    
    # Dictionary to store summary counts
    # Format: {filename: count}
    file_counts = defaultdict(int)
    
    parsed_files = find_parsed_files()
    print(f"Found {len(parsed_files)} parsed files to filter...")
    
    for file_path in parsed_files:
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}")
        
        try:
            df = pd.read_csv(file_path)
            original_count = len(df)
            
            # Determine the main field (cihui or hanzi) based on filename
            if 'cihui' in file_path:
                main_field = 'cihui'
            elif 'hanzi' in file_path:
                main_field = 'hanzi'
            else:
                print(f"Warning: Could not determine field type for {file_path}")
                continue
            
            # Filter rows that contain references to multiple-pinyin ref_cihui
            filtered_rows = []
            
            for idx, row in df.iterrows():
                definition = row.get('definition', '')
                
                if pd.notna(definition):
                    # Check if this definition contains references to multiple-pinyin ref_cihui
                    for ref_cihui in multiple_pinyin_set:
                        # Look for patterns like "ref_cihui①", "ref_cihui②", etc.
                        # This includes both circled numbers and regular numbers
                        patterns_to_check = [
                            f"{ref_cihui}①", f"{ref_cihui}②", f"{ref_cihui}③", f"{ref_cihui}④", f"{ref_cihui}⑤",
                            f"{ref_cihui}⑥", f"{ref_cihui}⑦", f"{ref_cihui}⑧", f"{ref_cihui}⑨", f"{ref_cihui}⑩",
                            f"{ref_cihui}1", f"{ref_cihui}2", f"{ref_cihui}3", f"{ref_cihui}4", f"{ref_cihui}5",
                            f"{ref_cihui}6", f"{ref_cihui}7", f"{ref_cihui}8", f"{ref_cihui}9", f"{ref_cihui}10"
                        ]
                        
                        for pattern in patterns_to_check:
                            if pattern in definition:
                                # Found a reference to a multiple-pinyin ref_cihui
                                filtered_rows.append(row)
                                break  # Found one reference, no need to check other patterns
            
            # Store filtered rows
            if filtered_rows:
                filtered_data[filename] = filtered_rows
                file_counts[filename] = len(filtered_rows)
                print(f"  Found {len(filtered_rows)} rows with multiple-pinyin references (out of {original_count})")
            else:
                print(f"  No rows with multiple-pinyin references found")
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    return filtered_data, file_counts

def save_filtered_data(filtered_data, file_counts):
    """Save the filtered data to separate CSV files."""
    
    if not filtered_data:
        print("No data to save.")
        return
    
    # Create output directory
    output_dir = "jjhy_csv/multiple_pinyin_filtered_rows"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each file's filtered rows
    for filename, rows in filtered_data.items():
        if rows:
            df = pd.DataFrame(rows)
            output_file = os.path.join(output_dir, f"filtered_{filename}")
            df.to_csv(output_file, index=False)
            print(f"Saved: {output_file} ({len(rows)} rows)")
    
    # Save summary
    summary_data = []
    for filename, count in sorted(file_counts.items()):
        if count > 0:
            summary_data.append({
                'filename': filename,
                'filtered_rows_count': count
            })
    
    summary_df = pd.DataFrame(summary_data)
    summary_file = os.path.join(output_dir, "filtered_files_summary.csv")
    summary_df.to_csv(summary_file, index=False)
    print(f"\nSummary saved to: {summary_file}")
    
    # Save combined filtered data
    all_filtered_rows = []
    for rows in filtered_data.values():
        all_filtered_rows.extend(rows)
    
    if all_filtered_rows:
        combined_df = pd.DataFrame(all_filtered_rows)
        combined_file = os.path.join(output_dir, "all_filtered_rows_combined.csv")
        combined_df.to_csv(combined_file, index=False)
        print(f"Combined data saved to: {combined_file} ({len(all_filtered_rows)} total rows)")

def main():
    """Main function to filter rows with multiple-pinyin references."""
    
    print("=== Filtering Rows with Multiple-Pinyin References ===\n")
    
    # Step 1: Load the list of multiple-pinyin ref_cihui
    print("Step 1: Loading multiple-pinyin ref_cihui list...")
    multiple_pinyin_set = load_multiple_pinyin_ref_cihui()
    
    if not multiple_pinyin_set:
        print("No multiple-pinyin ref_cihui found. Exiting.")
        return
    
    print(f"Found {len(multiple_pinyin_set)} ref_cihui with multiple pinyin pronunciations")
    
    # Step 2: Filter parsed files to extract relevant rows
    print("\nStep 2: Filtering parsed files...")
    filtered_data, file_counts = filter_multiple_pinyin_rows(multiple_pinyin_set)
    
    # Step 3: Generate summary
    print(f"\n=== FILTERING RESULTS ===")
    
    total_filtered = sum(file_counts.values())
    files_with_data = len([f for f, c in file_counts.items() if c > 0])
    
    print(f"Total filtered rows: {total_filtered}")
    print(f"Files containing filtered rows: {files_with_data}")
    
    if file_counts:
        print(f"\nBreakdown by file:")
        for filename, count in sorted(file_counts.items()):
            if count > 0:
                print(f"  {filename}: {count} rows")
    
    # Step 4: Save filtered data
    print(f"\nStep 3: Saving filtered data...")
    save_filtered_data(filtered_data, file_counts)
    
    print("\n=== Filtering Complete ===")

if __name__ == "__main__":
    main()
