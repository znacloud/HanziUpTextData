#!/usr/bin/env python3
"""
Script to find duplicated examples in hanzi_examples_v7.csv
Saves duplicated examples to others/duplicated_examples.csv
"""

import pandas as pd
import os
from collections import defaultdict

def find_duplicated_examples():
    # Read the CSV file
    input_file = "database_csv/hanzi_examples_v7.csv"
    output_file = "others/duplicated_examples.csv"
    
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Find duplicates based on Chinese text (example_cn)
    print("\nFinding duplicates based on Chinese text (example_cn)...")
    duplicates_by_cn = df[df.duplicated(subset=['example_cn'], keep=False)]
    
    
    # Combine all duplicates and remove duplicates from the combined result
    all_duplicates = pd.concat([
        duplicates_by_cn
    ]).drop_duplicates()
    
    # Sort by Chinese text for easier review
    all_duplicates = all_duplicates.sort_values(['example_cn', 'definition_id'])
    
    print(f"\nFound {len(all_duplicates)} rows with duplicates")
    
    # Create detailed analysis
    analysis = []
    
    # Group by Chinese text
    cn_groups = df.groupby('example_cn').filter(lambda x: len(x) > 1)
    for cn_text, group in cn_groups.groupby('example_cn'):
        analysis.append({
            'duplicate_type': 'Chinese text',
            'duplicate_value': cn_text,
            'count': len(group),
            'definition_ids': ','.join(map(str, group['definition_id'].tolist())),
            'example_sns': ','.join(map(str, group['example_sn'].tolist()))
        })

    
    
    # Create analysis DataFrame
    analysis_df = pd.DataFrame(analysis)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save results
    print(f"\nSaving duplicated examples to {output_file}...")
    all_duplicates.to_csv(output_file, index=False)
    
    # Save analysis
    analysis_file = "others/duplicate_analysis.csv"
    print(f"Saving duplicate analysis to {analysis_file}...")
    analysis_df.to_csv(analysis_file, index=False)
    
    # Print summary
    print(f"\nSummary:")
    print(f"- Total rows with duplicates: {len(all_duplicates)}")
    print(f"- Duplicates by Chinese text: {len(duplicates_by_cn)}")
    print(f"- Unique duplicate groups: {len(analysis_df)}")
    
    print(f"\nResults saved to:")
    print(f"- {output_file}")
    print(f"- {analysis_file}")

if __name__ == "__main__":
    find_duplicated_examples() 