#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to filter topic data based on hanzi existence in core hanzi pinyin file.
For each row in full_topic_parsed.csv, check if the "item" value exists in 
the "hanzi" column of jjhy_core_hanzi_pinyin.csv.
"""

import pandas as pd
import os
from pathlib import Path

def main():
    # File paths
    topic_file = "jjhy_csv/topic/full_topic_parsed.csv"
    hanzi_pinyin_file = "database_csv/jjhy_core_hanzi_pinyin.csv"
    output_file = "jjhy_csv/topic/hanzi_topic_filtered.csv"
    
    print("Loading topic data...")
    # Load topic data
    topic_df = pd.read_csv(topic_file)
    print(f"Loaded {len(topic_df)} topic rows")
    
    print("Loading hanzi pinyin data...")
    # Load hanzi pinyin data
    hanzi_df = pd.read_csv(hanzi_pinyin_file)
    print(f"Loaded {len(hanzi_df)} hanzi pinyin rows")
    
    # Get unique hanzi values from the core file
    valid_hanzi = set(hanzi_df['hanzi'].unique())
    print(f"Found {len(valid_hanzi)} unique hanzi characters")
    
    # Filter topic data - keep only rows where item exists in valid_hanzi
    print("Filtering topic data...")
    filtered_df = topic_df[topic_df['item'].isin(valid_hanzi)]
    
    print(f"Original topic rows: {len(topic_df)}")
    print(f"Filtered topic rows: {len(filtered_df)}")
    print(f"Removed {len(topic_df) - len(filtered_df)} rows")
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save filtered data
    print(f"Saving filtered data to {output_file}...")
    filtered_df.to_csv(output_file, index=False, encoding='utf-8')
    
    # Show some statistics
    print("\nFiltering statistics:")
    print(f"Items found in core hanzi: {len(filtered_df)}")
    print(f"Items not found in core hanzi: {len(topic_df) - len(filtered_df)}")
    
    # Show some examples of filtered items
    if len(filtered_df) > 0:
        print(f"\nSample filtered items:")
        sample_items = filtered_df['item'].head(10).tolist()
        for item in sample_items:
            print(f"  - {item}")
    
    # Show some examples of removed items
    removed_df = topic_df[~topic_df['item'].isin(valid_hanzi)]
    if len(removed_df) > 0:
        print(f"\nSample removed items:")
        sample_removed = removed_df['item'].head(10).tolist()
        for item in sample_removed:
            print(f"  - {item}")
    
    print(f"\nFiltering complete! Results saved to {output_file}")

if __name__ == "__main__":
    main()
