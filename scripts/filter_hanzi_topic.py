#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to filter rows in hanzi_topic_filtered.csv whose parent_category 
is in hanzi_topic_name_selected.csv
"""

import pandas as pd
import os

def main():
    # Define file paths
    base_dir = "jjhy_csv/topic"
    filtered_file = os.path.join(base_dir, "hanzi_topic_filtered.csv")
    selected_file = os.path.join(base_dir, "hanzi_topic_name_selected.csv")
    output_file = os.path.join(base_dir, "hanzi_topic_manual_selected_v2.csv")
    
    print("Reading hanzi_topic_name_selected.csv...")
    # Read the selected parent categories
    selected_df = pd.read_csv(selected_file, encoding='utf-8')
    selected_parent_categories = set(selected_df['parent_category'].tolist())
    
    print(f"Found {len(selected_parent_categories)} selected parent categories:")
    for cat in sorted(selected_parent_categories):
        print(f"  - {cat}")
    
    print("\nReading hanzi_topic_filtered.csv...")
    # Read the filtered data
    filtered_df = pd.read_csv(filtered_file, encoding='utf-8')
    print(f"Original file has {len(filtered_df)} rows")
    
    # Filter rows where parent_category is in the selected list
    print("\nFiltering rows...")
    filtered_result = filtered_df[filtered_df['parent_category'].isin(selected_parent_categories)]
    
    print(f"Filtered result has {len(filtered_result)} rows")
    
    # Save the result
    print(f"\nSaving result to {output_file}...")
    filtered_result.to_csv(output_file, index=False, encoding='utf-8')
    
    # Print summary statistics
    print("\nSummary by parent_category:")
    summary = filtered_result.groupby('parent_category').size().sort_values(ascending=False)
    for parent_cat, count in summary.items():
        print(f"  {parent_cat}: {count} rows")
    
    print(f"\nTotal rows in output: {len(filtered_result)}")
    print("Filtering completed successfully!")

if __name__ == "__main__":
    main()
