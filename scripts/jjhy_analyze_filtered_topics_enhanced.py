#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced script to analyze filtered topics and extract root/parent categories to separate files.
Provides comprehensive statistics and creates organized category files.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os

def load_data():
    """Load the filtered topic data"""
    file_path = "jjhy_csv/topic/hanzi_topic_filtered.csv"
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Data loaded successfully! Shape: {df.shape}")
    return df

def extract_root_categories(df):
    """Extract root categories to a separate file with detailed statistics"""
    print("\n" + "="*60)
    print("EXTRACTING ROOT CATEGORIES")
    print("="*60)
    
    # Group by root category and get statistics
    root_stats = df.groupby('root_category').agg({
        'parent_category': 'nunique',
        'category': 'nunique',
        'item': 'count'
    }).rename(columns={
        'parent_category': 'parent_category_count',
        'category': 'leaf_category_count',
        'item': 'total_items'
    }).sort_values('total_items', ascending=False)
    
    # Save root categories to CSV
    output_file = "jjhy_csv/topic/root_categories_detailed.csv"
    root_stats.to_csv(output_file, encoding='utf-8')
    print(f"Root categories saved to: {output_file}")
    
    # Display statistics
    print(f"\nTotal root categories: {len(root_stats)}")
    print(f"\nTop 10 root categories by item count:")
    for i, (cat, row) in enumerate(root_stats.head(10).iterrows(), 1):
        print(f"  {i:2d}. {cat}")
        print(f"      Items: {row['total_items']:,}")
        print(f"      Parent categories: {row['parent_category_count']}")
        print(f"      Leaf categories: {row['leaf_category_count']}")
    
    return root_stats

def extract_parent_categories(df):
    """Extract parent categories to a separate file with detailed statistics"""
    print("\n" + "="*60)
    print("EXTRACTING PARENT CATEGORIES")
    print("="*60)
    
    # Group by parent category and get statistics
    parent_stats = df.groupby('parent_category').agg({
        'root_category': 'first',
        'category': 'nunique',
        'item': 'count'
    }).rename(columns={
        'root_category': 'root_category',
        'category': 'leaf_category_count',
        'item': 'total_items'
    }).sort_values(['root_category', 'total_items'], ascending=[True, False])
    
    # Save parent categories to CSV
    output_file = "jjhy_csv/topic/parent_categories_detailed.csv"
    parent_stats.to_csv(output_file, encoding='utf-8')
    print(f"Parent categories saved to: {output_file}")
    
    # Display statistics
    print(f"\nTotal parent categories: {len(parent_stats)}")
    print(f"\nTop 15 parent categories by item count:")
    # Show top 15 by total_items for display purposes
    top_15 = parent_stats.sort_values('total_items', ascending=False).head(15)
    for i, (cat, row) in enumerate(top_15.iterrows(), 1):
        print(f"  {i:2d}. {cat}")
        print(f"      Root: {row['root_category']}")
        print(f"      Items: {row['total_items']:,}")
        print(f"      Leaf categories: {row['leaf_category_count']}")
    
    return parent_stats

def extract_leaf_categories(df):
    """Extract leaf categories to a separate file with detailed statistics"""
    print("\n" + "="*60)
    print("EXTRACTING LEAF CATEGORIES")
    print("="*60)
    
    # Group by leaf category and get statistics
    leaf_stats = df.groupby('category').agg({
        'root_category': 'first',
        'parent_category': 'first',
        'item': 'count'
    }).rename(columns={
        'root_category': 'root_category',
        'parent_category': 'parent_category',
        'item': 'total_items'
    }).sort_values('total_items', ascending=False)
    
    # Save leaf categories to CSV (top 1000 to avoid huge file)
    output_file = "jjhy_csv/topic/leaf_categories_top1000.csv"
    leaf_stats.head(1000).to_csv(output_file, encoding='utf-8')
    print(f"Top 1000 leaf categories saved to: {output_file}")
    
    # Display statistics
    print(f"\nTotal leaf categories: {len(leaf_stats)}")
    print(f"\nTop 20 leaf categories by item count:")
    for i, (cat, row) in enumerate(leaf_stats.head(20).iterrows(), 1):
        print(f"  {i:2d}. {cat}")
        print(f"      Root: {row['root_category']}")
        print(f"      Parent: {row['parent_category']}")
        print(f"      Items: {row['total_items']:,}")
    
    return leaf_stats

def generate_comprehensive_report(df, root_stats, parent_stats, leaf_stats):
    """Generate a comprehensive statistics report"""
    print("\n" + "="*60)
    print("GENERATING COMPREHENSIVE REPORT")
    print("="*60)
    
    output_file = "jjhy_csv/topic/comprehensive_topics_report.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("COMPREHENSIVE FILTERED TOPICS ANALYSIS REPORT\n")
        f.write("="*60 + "\n\n")
        
        # Dataset overview
        f.write("DATASET OVERVIEW\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total rows: {len(df):,}\n")
        f.write(f"Total columns: {len(df.columns)}\n")
        f.write(f"File size: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB\n")
        f.write(f"Unique items: {df['item'].nunique():,}\n\n")
        
        # Category structure
        f.write("CATEGORY STRUCTURE\n")
        f.write("-" * 30 + "\n")
        f.write(f"Root categories: {len(root_stats):,}\n")
        f.write(f"Parent categories: {len(parent_stats):,}\n")
        f.write(f"Leaf categories: {len(leaf_stats):,}\n\n")
        
        # Root categories summary
        f.write("ROOT CATEGORIES SUMMARY\n")
        f.write("-" * 30 + "\n")
        for i, (cat, row) in enumerate(root_stats.iterrows(), 1):
            f.write(f"{i:2d}. {cat}\n")
            f.write(f"    Items: {row['total_items']:,}\n")
            f.write(f"    Parent categories: {row['parent_category_count']}\n")
            f.write(f"    Leaf categories: {row['leaf_category_count']}\n\n")
        
        # Parent categories summary (top 50)
        f.write("PARENT CATEGORIES SUMMARY (Top 50)\n")
        f.write("-" * 40 + "\n")
        for i, (cat, row) in enumerate(parent_stats.head(50).iterrows(), 1):
            f.write(f"{i:2d}. {cat}\n")
            f.write(f"    Root: {row['root_category']}\n")
            f.write(f"    Items: {row['total_items']:,}\n")
            f.write(f"    Leaf categories: {row['leaf_category_count']}\n\n")
        
        # Leaf categories summary (top 100)
        f.write("LEAF CATEGORIES SUMMARY (Top 100)\n")
        f.write("-" * 40 + "\n")
        for i, (cat, row) in enumerate(leaf_stats.head(100).iterrows(), 1):
            f.write(f"{i:3d}. {cat}\n")
            f.write(f"     Root: {row['root_category']}\n")
            f.write(f"     Parent: {row['parent_category']}\n")
            f.write(f"     Items: {row['total_items']:,}\n\n")
        
        # Hierarchical analysis
        f.write("HIERARCHICAL ANALYSIS\n")
        f.write("-" * 30 + "\n")
        
        # Root categories with most subcategories
        f.write("Root categories with most parent categories:\n")
        root_by_parents = root_stats.sort_values('parent_category_count', ascending=False)
        for i, (cat, row) in enumerate(root_by_parents.head(10).iterrows(), 1):
            f.write(f"  {i:2d}. {cat}: {row['parent_category_count']} parent categories\n")
        
        f.write("\nParent categories with most leaf categories:\n")
        parent_by_leaves = parent_stats.sort_values('leaf_category_count', ascending=False)
        for i, (cat, row) in enumerate(parent_by_leaves.head(10).iterrows(), 1):
            f.write(f"  {i:2d}. {cat}: {row['leaf_category_count']} leaf categories\n")
        
        # Item distribution analysis
        f.write("\nITEM DISTRIBUTION ANALYSIS\n")
        f.write("-" * 30 + "\n")
        
        # Item length analysis
        df['item_length'] = df['item'].str.len()
        length_counts = df['item_length'].value_counts().sort_index()
        f.write("Item length distribution:\n")
        for length, count in length_counts.items():
            percentage = (count / len(df)) * 100
            f.write(f"  {length} character(s): {count:,} items ({percentage:.1f}%)\n")
        
        # Cross-category items
        multi_category_items = df.groupby('item')['category'].nunique()
        multi_cat_count = (multi_category_items > 1).sum()
        f.write(f"\nItems appearing in multiple categories: {multi_cat_count:,}\n")
        
        # Serial number analysis
        f.write("\nSERIAL NUMBER ANALYSIS\n")
        f.write("-" * 30 + "\n")
        f.write(f"Root SN range: {df['root_sn'].min()} to {df['root_sn'].max()}\n")
        f.write(f"Parent SN range: {df['parent_sn'].min()} to {df['parent_sn'].max()}\n")
        f.write(f"Leaf SN range: {df['sn'].min()} to {df['sn'].max()}\n")
        
        # Item rank analysis
        f.write("\nITEM RANK ANALYSIS\n")
        f.write("-" * 30 + "\n")
        df['item_rank_numeric'] = pd.to_numeric(df['item_rank'], errors='coerce')
        valid_ranks = df['item_rank_numeric'].dropna()
        if len(valid_ranks) > 0:
            f.write(f"Rank range: {valid_ranks.min():.0f} to {valid_ranks.max():.0f}\n")
            f.write(f"Mean rank: {valid_ranks.mean():.1f}\n")
            f.write(f"Median rank: {valid_ranks.median():.1f}\n")
            
            # Rank distribution
            rank_ranges = [
                (0, 100, "0-100"),
                (101, 500, "101-500"),
                (501, 1000, "501-1000"),
                (1001, 5000, "1001-5000"),
                (5001, 10000, "5001-10000"),
                (10001, float('inf'), "10001+")
            ]
            
            f.write("\nRank distribution:\n")
            for min_rank, max_rank, label in rank_ranges:
                if max_rank == float('inf'):
                    count = (valid_ranks >= min_rank).sum()
                else:
                    count = ((valid_ranks >= min_rank) & (valid_ranks <= max_rank)).sum()
                percentage = (count / len(valid_ranks)) * 100
                f.write(f"  {label}: {count:,} items ({percentage:.1f}%)\n")
    
    print(f"Comprehensive report saved to: {output_file}")

def main():
    """Main function to run all analyses and extractions"""
    print("ENHANCED FILTERED TOPICS ANALYSIS AND EXTRACTION")
    print("="*60)
    
    try:
        # Load data
        df = load_data()
        
        # Extract categories to separate files
        root_stats = extract_root_categories(df)
        parent_stats = extract_parent_categories(df)
        leaf_stats = extract_leaf_categories(df)
        
        # Generate comprehensive report
        generate_comprehensive_report(df, root_stats, parent_stats, leaf_stats)
        
        print(f"\n" + "="*60)
        print("ANALYSIS AND EXTRACTION COMPLETE!")
        print("="*60)
        print(f"Files generated:")
        print(f"  - Root categories: jjhy_csv/topic/root_categories_detailed.csv")
        print(f"  - Parent categories: jjhy_csv/topic/parent_categories_detailed.csv")
        print(f"  - Leaf categories: jjhy_csv/topic/leaf_categories_top1000.csv")
        print(f"  - Comprehensive report: jjhy_csv/topic/comprehensive_topics_report.txt")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
