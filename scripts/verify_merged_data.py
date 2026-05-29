#!/usr/bin/env python3
"""
Verification script to show examples of merged entries and compare before/after.
"""

import json
from collections import defaultdict

def load_data(file_path):
    """Load JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_examples_of_merged_entries(original_data, merged_data):
    """Find and display examples of entries that were merged."""
    print("="*60)
    print("EXAMPLES OF MERGED ENTRIES")
    print("="*60)
    
    # Convert merged data to a lookup format
    merged_lookup = {}
    for entry in merged_data:
        hanzi = list(entry.keys())[0]
        merged_lookup[hanzi] = entry[hanzi]
    
    # Find examples where original had multiple entries for same hanzi
    hanzi_counts = defaultdict(list)
    for entry in original_data:
        hanzi = list(entry.keys())[0]
        hanzi_counts[hanzi].append(entry)
    
    # Show examples of merged entries
    examples_shown = 0
    for hanzi, entries in hanzi_counts.items():
        if len(entries) > 1 and examples_shown < 5:  # Show first 5 examples
            print(f"\n🔤 Hanzi: {hanzi}")
            print(f"   Original entries: {len(entries)}")
            print(f"   Merged into: {len(merged_lookup[hanzi])} pinyin entries")
            
            # Show original structure
            print("   Original structure:")
            for i, entry in enumerate(entries, 1):
                pinyin_entries = entry[hanzi]
                print(f"     Entry {i}: {len(pinyin_entries)} pinyin entries")
                for j, pinyin_entry in enumerate(pinyin_entries):
                    print(f"       Pinyin {j+1}: {pinyin_entry['pinyin']} ({len(pinyin_entry['definitions'])} definitions)")
            
            # Show merged structure
            print("   Merged structure:")
            for j, pinyin_entry in enumerate(merged_lookup[hanzi]):
                print(f"     Pinyin {j+1}: {pinyin_entry['pinyin']} ({len(pinyin_entry['definitions'])} definitions)")
            
            examples_shown += 1
    
    # Find examples of pinyin merging
    print(f"\n" + "="*60)
    print("EXAMPLES OF PINYIN MERGING")
    print("="*60)
    
    pinyin_examples_shown = 0
    for hanzi, pinyin_entries in merged_lookup.items():
        if pinyin_examples_shown >= 3:
            break
            
        # Check if this hanzi had pinyin merging
        pinyin_counts = defaultdict(list)
        for entry in pinyin_entries:
            pinyin_counts[entry['pinyin']].append(entry)
        
        for pinyin, entries in pinyin_counts.items():
            if len(entries) > 1 and pinyin_examples_shown < 3:
                print(f"\n🔤 Hanzi: {hanzi}")
                print(f"   Pinyin: {pinyin}")
                print(f"   Original entries with this pinyin: {len(entries)}")
                
                # Show definitions from each original entry
                total_definitions = 0
                for i, entry in enumerate(entries):
                    print(f"     Entry {i+1}: {len(entry['definitions'])} definitions")
                    total_definitions += len(entry['definitions'])
                
                # Find the merged entry
                merged_entry = None
                for entry in pinyin_entries:
                    if entry['pinyin'] == pinyin:
                        merged_entry = entry
                        break
                
                if merged_entry:
                    print(f"   Merged into: {len(merged_entry['definitions'])} unique definitions")
                    print(f"   Duplicates removed: {total_definitions - len(merged_entry['definitions'])}")
                
                pinyin_examples_shown += 1
                break

def show_statistics(original_data, merged_data):
    """Show detailed statistics about the merging process."""
    print(f"\n" + "="*60)
    print("DETAILED STATISTICS")
    print("="*60)
    
    # Original statistics
    original_entries = len(original_data)
    original_hanzi = len(set(list(entry.keys())[0] for entry in original_data))
    original_pinyin_count = sum(len(entry[list(entry.keys())[0]]) for entry in original_data)
    
    # Merged statistics
    merged_entries = len(merged_data)
    merged_hanzi = len(set(list(entry.keys())[0] for entry in merged_data))
    merged_pinyin_count = sum(len(entry[list(entry.keys())[0]]) for entry in merged_data)
    
    print(f"Original Data:")
    print(f"  Total entries: {original_entries:,}")
    print(f"  Unique hanzi: {original_hanzi:,}")
    print(f"  Total pinyin entries: {original_pinyin_count:,}")
    
    print(f"\nMerged Data:")
    print(f"  Total entries: {merged_entries:,}")
    print(f"  Unique hanzi: {merged_hanzi:,}")
    print(f"  Total pinyin entries: {merged_pinyin_count:,}")
    
    print(f"\nReduction:")
    print(f"  Entries reduced: {original_entries - merged_entries:,} ({((original_entries - merged_entries) / original_entries * 100):.1f}%)")
    print(f"  Pinyin entries reduced: {original_pinyin_count - merged_pinyin_count:,} ({((original_pinyin_count - merged_pinyin_count) / original_pinyin_count * 100):.1f}%)")

def main():
    """Main function."""
    original_file = "raw_data/xdhy_entries_parsed_filtered.json"
    merged_file = "raw_data/xdhy_entries_parsed_filtered_merged.json"
    
    try:
        print("Loading original data...")
        original_data = load_data(original_file)
        
        print("Loading merged data...")
        merged_data = load_data(merged_file)
        
        # Show statistics
        show_statistics(original_data, merged_data)
        
        # Show examples
        find_examples_of_merged_entries(original_data, merged_data)
        
        print(f"\n✅ Verification completed!")
        
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 