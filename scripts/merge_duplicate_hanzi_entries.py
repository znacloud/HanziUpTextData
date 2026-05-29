#!/usr/bin/env python3
"""
Script to merge duplicate hanzi entries and then merge duplicate pinyin entries
while preserving different definitions.

This script:
1. Loads the xdhy_entries_parsed_filtered.json file
2. Merges entries with the same hanzi character
3. For each hanzi, merges entries with the same pinyin but different definitions
4. Saves the merged result to a new JSON file
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Any

def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """Load JSON data from file."""
    print(f"Loading data from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} entries")
    return data

def merge_hanzi_entries(data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Merge entries with the same hanzi character.
    
    Args:
        data: List of dictionaries where each dict has one key (hanzi) and value (pinyin/definitions)
    
    Returns:
        Dictionary with hanzi as keys and merged pinyin/definitions as values
    """
    print("Merging duplicate hanzi entries...")
    
    # Group entries by hanzi
    hanzi_groups = defaultdict(list)
    
    for entry in data:
        hanzi = list(entry.keys())[0]
        pinyin_entries = entry[hanzi]
        hanzi_groups[hanzi].extend(pinyin_entries)
    
    print(f"Found {len(hanzi_groups)} unique hanzi characters")
    
    # Convert defaultdict to regular dict
    merged_hanzi = dict(hanzi_groups)
    
    return merged_hanzi

def merge_pinyin_entries(hanzi_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    For each hanzi, merge entries with the same pinyin but different definitions.
    
    Args:
        hanzi_data: Dictionary with hanzi as keys and list of pinyin/definitions as values
    
    Returns:
        Dictionary with merged pinyin entries for each hanzi
    """
    print("Merging duplicate pinyin entries...")
    
    merged_data = {}
    
    for hanzi, pinyin_entries in hanzi_data.items():
        # Group pinyin entries by pinyin
        pinyin_groups = defaultdict(list)
        
        for entry in pinyin_entries:
            pinyin = entry['pinyin']
            pinyin_groups[pinyin].append(entry)
        
        # Merge entries with same pinyin
        merged_pinyin_entries = []
        
        for pinyin, entries in pinyin_groups.items():
            if len(entries) == 1:
                # No duplicates, keep as is
                merged_pinyin_entries.append(entries[0])
            else:
                # Merge multiple entries with same pinyin
                merged_entry = {
                    'pinyin': pinyin,
                    'definitions': []
                }
                
                # Collect all definitions from all entries
                for entry in entries:
                    merged_entry['definitions'].extend(entry['definitions'])
                
                # Remove duplicate definitions (based on content)
                unique_definitions = []
                seen_definitions = set()
                
                for definition in merged_entry['definitions']:
                    # Create a key for comparison (using Chinese definition as primary)
                    def_key = definition.get('cn', '')
                    if def_key not in seen_definitions:
                        seen_definitions.add(def_key)
                        unique_definitions.append(definition)
                
                merged_entry['definitions'] = unique_definitions
                merged_pinyin_entries.append(merged_entry)
        
        merged_data[hanzi] = merged_pinyin_entries
    
    return merged_data

def analyze_merging_results(original_data: List[Dict[str, Any]], 
                          merged_hanzi: Dict[str, List[Dict[str, Any]]],
                          final_merged: Dict[str, List[Dict[str, Any]]]) -> None:
    """Analyze and print statistics about the merging process."""
    print("\n" + "="*50)
    print("MERGING ANALYSIS")
    print("="*50)
    
    # Original statistics
    original_entries = len(original_data)
    original_hanzi = len(set(list(entry.keys())[0] for entry in original_data))
    
    # After hanzi merging
    merged_hanzi_count = len(merged_hanzi)
    
    # After pinyin merging
    final_hanzi_count = len(final_merged)
    
    # Count total pinyin entries
    original_pinyin_count = sum(len(entry[list(entry.keys())[0]]) for entry in original_data)
    merged_pinyin_count = sum(len(entries) for entries in merged_hanzi.values())
    final_pinyin_count = sum(len(entries) for entries in final_merged.values())
    
    print(f"Original data:")
    print(f"  - Total entries: {original_entries}")
    print(f"  - Unique hanzi: {original_hanzi}")
    print(f"  - Total pinyin entries: {original_pinyin_count}")
    
    print(f"\nAfter hanzi merging:")
    print(f"  - Unique hanzi: {merged_hanzi_count}")
    print(f"  - Total pinyin entries: {merged_pinyin_count}")
    print(f"  - Hanzi entries reduced by: {original_entries - merged_hanzi_count}")
    
    print(f"\nAfter pinyin merging:")
    print(f"  - Unique hanzi: {final_hanzi_count}")
    print(f"  - Total pinyin entries: {final_pinyin_count}")
    print(f"  - Pinyin entries reduced by: {merged_pinyin_count - final_pinyin_count}")
    
    print(f"\nTotal reduction:")
    print(f"  - Hanzi entries: {original_entries - final_hanzi_count} ({((original_entries - final_hanzi_count) / original_entries * 100):.1f}%)")
    print(f"  - Pinyin entries: {original_pinyin_count - final_pinyin_count} ({((original_pinyin_count - final_pinyin_count) / original_pinyin_count * 100):.1f}%)")

def save_merged_data(data: Dict[str, List[Dict[str, Any]]], output_path: str) -> None:
    """Save merged data to JSON file."""
    print(f"\nSaving merged data to {output_path}...")
    
    # Convert to list format to match original structure
    output_data = []
    for hanzi, pinyin_entries in data.items():
        output_data.append({hanzi: pinyin_entries})
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(output_data)} merged entries")

def main():
    """Main function to execute the merging process."""
    # File paths
    input_file = "raw_data/xdhy_entries_parsed_filtered.json"
    output_file = "raw_data/xdhy_entries_parsed_filtered_merged.json"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found!")
        return
    
    try:
        # Load original data
        original_data = load_json_data(input_file)
        
        # Step 1: Merge duplicate hanzi entries
        merged_hanzi = merge_hanzi_entries(original_data)
        
        # Step 2: Merge duplicate pinyin entries for each hanzi
        final_merged = merge_pinyin_entries(merged_hanzi)
        
        # Analyze results
        analyze_merging_results(original_data, merged_hanzi, final_merged)
        
        # Save merged data
        save_merged_data(final_merged, output_file)
        
        print(f"\n✅ Merging completed successfully!")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during merging process: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 