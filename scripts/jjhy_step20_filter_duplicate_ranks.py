#!/usr/bin/env python3
"""
Script to filter rows where rank appears at least twice in CSV files.

This script processes all CSV files in the 'jjhy_csv/final_merged/' directory
and creates filtered versions containing only rows where the rank value
appears at least twice in the original file.
"""

import pandas as pd
import os
from pathlib import Path
from collections import Counter


def filter_duplicate_ranks(input_file_path, output_file_path):
    """
    Filter CSV file to keep only rows where rank appears at least twice.
    
    Args:
        input_file_path (str): Path to the input CSV file
        output_file_path (str): Path to save the filtered CSV file
        
    Returns:
        tuple: (total_rows, filtered_rows, duplicate_ranks_count)
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file_path)
        
        if 'rank' not in df.columns:
            print(f"Warning: 'rank' column not found in {input_file_path}")
            return 0, 0, 0
        
        # Count occurrences of each rank
        rank_counts = Counter(df['rank'])
        
        # Find ranks that appear at least twice
        duplicate_ranks = {rank for rank, count in rank_counts.items() if count >= 2}
        
        # Filter dataframe to keep only rows with duplicate ranks
        filtered_df = df[df['rank'].isin(duplicate_ranks)]
        
        # Save the filtered dataframe
        filtered_df.to_csv(output_file_path, index=False)
        
        total_rows = len(df)
        filtered_rows = len(filtered_df)
        duplicate_ranks_count = len(duplicate_ranks)
        
        print(f"Processed {input_file_path}:")
        print(f"  Total rows: {total_rows}")
        print(f"  Filtered rows: {filtered_rows}")
        print(f"  Duplicate ranks: {duplicate_ranks_count}")
        print(f"  Output saved to: {output_file_path}")
        print()
        
        return total_rows, filtered_rows, duplicate_ranks_count
        
    except Exception as e:
        print(f"Error processing {input_file_path}: {str(e)}")
        return 0, 0, 0


def main():
    """Main function to process all CSV files in the final_merged directory."""
    
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    input_dir = project_root / "jjhy_csv" / "core_csv"
    output_dir = project_root / "jjhy_csv" / "core_csv_rank_duplicates"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Get all CSV files in the input directory
    csv_files = list(input_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print("=" * 50)
    
    total_stats = {
        'files_processed': 0,
        'total_input_rows': 0,
        'total_output_rows': 0,
        'total_duplicate_ranks': 0
    }
    
    # Process each CSV file
    for csv_file in sorted(csv_files):
        input_path = csv_file
        output_path = output_dir / csv_file.name
        
        total_rows, filtered_rows, duplicate_ranks_count = filter_duplicate_ranks(
            str(input_path), str(output_path)
        )
        
        if total_rows > 0:  # Only count successfully processed files
            total_stats['files_processed'] += 1
            total_stats['total_input_rows'] += total_rows
            total_stats['total_output_rows'] += filtered_rows
            total_stats['total_duplicate_ranks'] += duplicate_ranks_count
    
    # Print summary
    print("=" * 50)
    print("SUMMARY:")
    print(f"Files processed: {total_stats['files_processed']}")
    print(f"Total input rows: {total_stats['total_input_rows']:,}")
    print(f"Total output rows: {total_stats['total_output_rows']:,}")
    print(f"Total unique duplicate ranks: {total_stats['total_duplicate_ranks']:,}")
    print(f"Reduction ratio: {(1 - total_stats['total_output_rows'] / max(1, total_stats['total_input_rows'])):.2%}")


if __name__ == "__main__":
    main()
