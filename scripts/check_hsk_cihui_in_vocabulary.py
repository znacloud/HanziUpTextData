#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check if all cihui (vocabulary words) in hsk_word.csv 
exist in 现代汉语常用词表_2008_sorted.csv

This script will:
1. Load both CSV files
2. Extract all cihui from both files
3. Check which HSK cihui are missing from the vocabulary list
4. Generate a report with statistics and missing words
"""

import pandas as pd
import os
from pathlib import Path

def load_csv_files():
    """Load both CSV files and return their dataframes"""
    # Get the script directory and navigate to raw_data
    script_dir = Path(__file__).parent
    raw_data_dir = script_dir.parent / "raw_data"
    
    # Load HSK word CSV
    hsk_file = raw_data_dir / "hsk_word.csv"
    if not hsk_file.exists():
        raise FileNotFoundError(f"HSK word file not found: {hsk_file}")
    
    hsk_df = pd.read_csv(hsk_file)
    print(f"Loaded HSK word CSV: {len(hsk_df)} entries")
    
    # Load modern Chinese vocabulary list CSV
    vocab_file = raw_data_dir / "现代汉语常用词表_2008_sorted.csv"
    if not vocab_file.exists():
        raise FileNotFoundError(f"Vocabulary file not found: {vocab_file}")
    
    vocab_df = pd.read_csv(vocab_file)
    print(f"Loaded vocabulary CSV: {len(vocab_df)} entries")
    
    return hsk_df, vocab_df

def check_cihui_existence(hsk_df, vocab_df):
    """Check which HSK cihui exist in the vocabulary list"""
    # Extract cihui from both dataframes
    hsk_cihui = set(hsk_df['cihui'].dropna().astype(str))
    vocab_cihui = set(vocab_df['cihui'].dropna().astype(str))
    
    print(f"\nHSK unique cihui: {len(hsk_cihui)}")
    print(f"Vocabulary unique cihui: {len(vocab_cihui)}")
    
    # Find missing cihui
    missing_cihui = hsk_cihui - vocab_cihui
    existing_cihui = hsk_cihui & vocab_cihui
    
    print(f"HSK cihui found in vocabulary: {len(existing_cihui)}")
    print(f"HSK cihui missing from vocabulary: {len(missing_cihui)}")
    
    return missing_cihui, existing_cihui, hsk_cihui, vocab_cihui

def generate_detailed_report(hsk_df, missing_cihui, existing_cihui):
    """Generate a detailed report of missing and existing cihui"""
    print("\n" + "="*60)
    print("DETAILED REPORT")
    print("="*60)
    
    # Show some examples of existing cihui
    print(f"\nExamples of HSK cihui found in vocabulary (showing first 10):")
    existing_examples = list(existing_cihui)[:10]
    for cihui in existing_examples:
        hsk_info = hsk_df[hsk_df['cihui'] == cihui].iloc[0]
        print(f"  ✓ {cihui} (HSK Level {hsk_info['hsk_level']}, Pinyin: {hsk_info['pinyin']})")
    
    # Show missing cihui with details
    if missing_cihui:
        print(f"\nHSK cihui missing from vocabulary list:")
        missing_list = sorted(list(missing_cihui))
        for cihui in missing_list:
            hsk_info = hsk_df[hsk_df['cihui'] == cihui].iloc[0]
            print(f"  ✗ {cihui} (HSK Level {hsk_info['hsk_level']}, Pinyin: {hsk_info['pinyin']})")
    else:
        print("\n✓ All HSK cihui are found in the vocabulary list!")
    
    # Statistics by HSK level
    print(f"\nStatistics by HSK level:")
    for level in sorted(hsk_df['hsk_level'].unique()):
        level_cihui = set(hsk_df[hsk_df['hsk_level'] == level]['cihui'])
        level_missing = level_cihui & missing_cihui
        level_existing = level_cihui & existing_cihui
        print(f"  HSK Level {level}: {len(level_existing)} found, {len(level_missing)} missing")

def save_missing_cihui_report(hsk_df, missing_cihui):
    """Save missing cihui to a CSV file for further analysis"""
    if missing_cihui:
        script_dir = Path(__file__).parent
        output_file = script_dir / "missing_hsk_cihui_report.csv"
        
        missing_data = []
        for cihui in missing_cihui:
            hsk_info = hsk_df[hsk_df['cihui'] == cihui].iloc[0]
            missing_data.append({
                'cihui': cihui,
                'pinyin': hsk_info['pinyin'],
                'hsk_level': hsk_info['hsk_level'],
                'hsk_sn': hsk_info['hsk_sn']
            })
        
        missing_df = pd.DataFrame(missing_data)
        missing_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nMissing cihui report saved to: {output_file}")
    else:
        print("\nNo missing cihui to report!")

def main():
    """Main function to run the cihui existence check"""
    try:
        print("Checking HSK cihui existence in modern Chinese vocabulary list...")
        print("="*60)
        
        # Load CSV files
        hsk_df, vocab_df = load_csv_files()
        
        # Check cihui existence
        missing_cihui, existing_cihui, hsk_cihui, vocab_cihui = check_cihui_existence(hsk_df, vocab_df)
        
        # Generate detailed report
        generate_detailed_report(hsk_df, missing_cihui, existing_cihui)
        
        # Save missing cihui report
        save_missing_cihui_report(hsk_df, missing_cihui)
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        coverage_rate = (len(existing_cihui) / len(hsk_cihui)) * 100
        print(f"Coverage rate: {coverage_rate:.2f}% ({len(existing_cihui)}/{len(hsk_cihui)})")
        
        if missing_cihui:
            print(f"Missing words: {len(missing_cihui)}")
            print("Check the generated report for details.")
        else:
            print("✓ Perfect coverage! All HSK cihui are found in the vocabulary list.")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
