import pandas as pd
import re
import glob
from collections import defaultdict
from pinyin_utils import split_pinyin

def clean_pinyin(pinyin):
    """Clean pinyin by removing spaces and standardizing format"""
    if pd.isna(pinyin) or pinyin == '':
        return ''
    # Remove spaces and standardize
    return pinyin.strip()

def clean_hanzi(hanzi):
    """Clean hanzi by removing spaces and standardizing format"""
    if pd.isna(hanzi) or hanzi == '':
        return ''
    return hanzi.strip()

def clean_definition(definition):
    """Clean definition text"""
    if pd.isna(definition) or definition == '':
        return ''
    return definition.strip()

def clean_example(example):
    """Clean example text"""
    if pd.isna(example) or example == '':
        return ''
    return example.strip()

def clean_pos(pos):
    """Clean and standardize part of speech"""
    if pd.isna(pos) or pos == '':
        return ''
    
    pos_mapping = {
        '名': '名词',
        '动': '动词', 
        '形': '形容词',
        '副': '副词',
        '代': '代词',
        '介': '介词',
        '连': '连词',
        '助': '助词',
        '数': '数词',
        '量': '量词',
        '叹': '叹词',
        '拟声': '拟声词'
    }
    
    pos = pos.strip()
    return pos_mapping.get(pos, pos)

def get_hsk_level_data():
    hsk_level_data = pd.read_csv('raw_data/hsk_word.csv')
    hsk_level_data = hsk_level_data[['cihui','hsk_level']].drop_duplicates()
    return hsk_level_data

def separate_jjhy_csv(df,rank_number,TAG,hsk_level_data):
    """Separate jjhy_cihui_parsed_5000_filtered.csv into three files"""
    
    # Declare global variables
    global hanzi_id_counter, pinyin_id_counter, definition_id_counter, example_id_counter
    
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Clean the data
    df[TAG] = df[TAG].apply(clean_hanzi)
    df['pinyin'] = df['pinyin'].apply(clean_pinyin)
    df['definition'] = df['definition'].apply(clean_definition)
    df['example'] = df['example'].apply(clean_example)
    df['pos'] = df['pos'].apply(clean_pos)
    
    # Remove rows with empty hanzi or pinyin
    df = df[(df[TAG] != '') & (df['pinyin'] != '')]
    print(f"Rows after cleaning: {len(df)}")
    
    # 1. Create hanzi_pinyin file
    print("\nCreating hanzi_pinyin file...")
    hanzi_pinyin_data = []
    # hanzi_id_counter = 1
    # pinyin_id_counter = 1
    hanzi_to_id = {}
    pinyin_to_id = {}
    
    # Group by hanzi and pinyin combinations, keeping the minimum rank for each combination
    hanzi_pinyin_groups = df.groupby([TAG, 'pinyin']).agg({
        'rank': 'min',  # Use the minimum rank for each hanzi-pinyin combination
        'sn': 'min'
    }).reset_index()
    
    # Sort by rank first (frequency), then by hanzi to ensure consistent ordering
    hanzi_pinyin_groups = hanzi_pinyin_groups.sort_values(['rank', 'sn'])
    
    # Track pinyin_sn for each hanzi
    hanzi_pinyin_sn = defaultdict(int)
    
    for _, row in hanzi_pinyin_groups.iterrows():
        hanzi = row[TAG]
        pinyin = row['pinyin']
        rank = row['rank']
        
        # Keep the hanzi_id consistent and stable throughout files
        hanzi_id_counter = int(rank) + 50000 if TAG == 'cihui' else int(rank)
        # Assign hanzi_id
        if hanzi not in hanzi_to_id:
            hanzi_to_id[hanzi] = hanzi_id_counter
            # hanzi_id_counter += 1
        
        # Assign pinyin_id
        pinyin_key = f"{hanzi}_{pinyin}"
        if pinyin_key not in pinyin_to_id:
            pinyin_to_id[pinyin_key] = pinyin_id_counter
            pinyin_id_counter += 1
        
        # Increment pinyin_sn for this hanzi
        hanzi_pinyin_sn[hanzi] += 1
        
        hanzi_pinyin_data.append({
            'hanzi_id': hanzi_to_id[hanzi],
            'hanzi': hanzi,
            'frequency_rank': str(int(rank)) if pd.notna(rank) else '',  # Apply rank value
            'pinyin_id': pinyin_to_id[pinyin_key],
            'pinyin': pinyin,
            'pinyin_sn': hanzi_pinyin_sn[hanzi],  # Increment for each pinyin of the same hanzi
            # no need hsk_level for now
            # 'hsk_level': hsk_level_data[hsk_level_data['cihui'] == hanzi]['hsk_level'].values[0].astype(int) if not hsk_level_data[hsk_level_data['cihui'] == hanzi]['hsk_level'].empty else '',  # Not available in source data
        })
    
    hanzi_pinyin_df = pd.DataFrame(hanzi_pinyin_data)
    hanzi_pinyin_df.to_csv(f'jjhy_csv/core_csv_seperated/jjhy_{TAG}_pinyin_{rank_number}.csv', index=False)
    print(f"Created hanzi_pinyin file with {len(hanzi_pinyin_df)} rows")
    
    # 2. Create hanzi_definition file (remove duplicates)
    print("\nCreating hanzi_definition file...")
    definition_data = []
    # definition_id_counter = 1
    
    # Create a set to track unique definitions to avoid duplicates
    seen_definitions = set()
    
    # Track definition_sn for each pinyin_id
    pinyin_definition_sn = defaultdict(int)
    
    for _, row in df.iterrows():
        hanzi = row[TAG]
        pinyin = row['pinyin']
        definition = row['definition']
        definition_en = row['definition_en']
        pos = row['pos']
        ref_hanzi = row['ref_hanzi']
        ref_pinyin = row['ref_pinyin']
        
        if definition == '':
            continue
            
        # Create a unique key for definition to avoid duplicates
        definition_key = f"{hanzi}_{pinyin}_{definition}_{pos}"
        
        if definition_key in seen_definitions:
            continue  # Skip duplicate definitions
            
        seen_definitions.add(definition_key)
            
        # Get pinyin_id
        pinyin_key = f"{hanzi}_{pinyin}"
        pinyin_id = pinyin_to_id.get(pinyin_key, 1)
        
        # Increment definition_sn for this pinyin_id
        pinyin_definition_sn[pinyin_id] += 1
        
        definition_data.append({
            'definition_id': definition_id_counter,
            'pinyin_id': pinyin_id,
            # 'ref_hanzi': ref_hanzi,
            # 'ref_pinyin': ref_pinyin,
            'definition_sn': pinyin_definition_sn[pinyin_id],  # Increment for each definition of the same pinyin
            'pos': pos,
            'original_definition_cn': definition, #if ref_hanzi == '' or not isinstance(ref_pinyin, str) else f'【{ref_hanzi}({split_pinyin(0,ref_pinyin,ref_hanzi)[0].replace(r"\sr$", " er")})】{definition}',
            'definition_cn': definition if ref_hanzi == '' or not isinstance(ref_pinyin, str) else f'【{ref_hanzi}({split_pinyin(0,ref_pinyin,ref_hanzi)[0].replace(r"\sr$", " er")})】{definition}',
            'definition_en': definition_en
        })
        
        definition_id_counter += 1
    
    definition_df = pd.DataFrame(definition_data).drop(columns=['original_definition_cn'])
    definition_df.to_csv(f'jjhy_csv/core_csv_seperated/jjhy_{TAG}_definition_{rank_number}.csv', index=False)
    print(f"Created hanzi_definition file with {len(definition_df)} rows (duplicates removed)")
    definition_df = pd.DataFrame(definition_data)
    
    # 3. Create hanzi_examples file
    print("\nCreating hanzi_examples file...")
    example_data = []
    # example_id_counter = 1
    example_sn_counter = defaultdict(int)
    
    for _, row in df.iterrows():
        hanzi = row[TAG]
        pinyin = row['pinyin']
        example = row['example']
        definition = row['definition']
        pos = row['pos']
        
        if example == '' or definition == '':
            continue
            
        # Find the definition_id for this definition (using the deduplicated definition_df)
        definition_key = f"{hanzi}_{pinyin}_{definition}_{pos}"
        if definition_key not in seen_definitions:
            continue  # Skip if this definition was removed as duplicate
            
        # Find the definition_id by matching the unique combination
        definition_row = definition_df[
            (definition_df['original_definition_cn'] == definition) & 
            (definition_df['pinyin_id'] == pinyin_to_id.get(f"{hanzi}_{pinyin}", 1)) &
            (definition_df['pos'] == pos)
        ]
        
        if len(definition_row) == 0:
            continue
            
        definition_id = definition_row.iloc[0]['definition_id']
        
        # Increment example_sn for this definition
        example_sn_counter[definition_id] += 1
        
        example_data.append({
            'example_id': example_id_counter,
            'definition_id': definition_id,
            'example_sn': example_sn_counter[definition_id],
            'example_cn': example
        })
        example_id_counter += 1
    example_df = pd.DataFrame(example_data)
    example_df.to_csv(f'jjhy_csv/core_csv_seperated/jjhy_{TAG}_examples_{rank_number}.csv', index=False)
    print(f"Created hanzi_examples file with {len(example_df)} rows")
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Source file rows: {len(df)}")
    print(f"Unique hanzi-pinyin combinations: {len(hanzi_pinyin_df)}")
    print(f"Definitions (after deduplication): {len(definition_df)}")
    print(f"Examples: {len(example_df)}")
    print(f"Unique hanzi: {len(hanzi_to_id)}")
    print(f"Unique pinyin combinations: {len(pinyin_to_id)}")
    
    # Print some statistics about pinyin_sn and definition_sn
    print(f"\nPinyin SN statistics:")
    pinyin_sn_counts = hanzi_pinyin_df['pinyin_sn'].value_counts().sort_index()
    for sn, count in pinyin_sn_counts.items():
        print(f"  pinyin_sn={sn}: {count} entries")
    
    print(f"\nDefinition SN statistics:")
    definition_sn_counts = definition_df['definition_sn'].value_counts().sort_index()
    for sn, count in definition_sn_counts.items():
        print(f"  definition_sn={sn}: {count} entries")
    
    # Save mapping for reference
    mapping_data = {
        'hanzi_to_id': hanzi_to_id,
        'pinyin_to_id': pinyin_to_id
    }
    
    print(f"\nFiles created for rank {rank_number}:")
    print(f"- jjhy_csv/core_csv_seperated/jjhy_{TAG}_pinyin_{rank_number}.csv")
    print(f"- jjhy_csv/core_csv_seperated/jjhy_{TAG}_definition_{rank_number}.csv") 
    print(f"- jjhy_csv/core_csv_seperated/jjhy_{TAG}_examples_{rank_number}.csv")





# global unique id counters
hanzi_id_counter = 1
pinyin_id_counter = 1
definition_id_counter = 1
example_id_counter = 1

if __name__ == "__main__":
    """Separate all jjhy_cihui_parsed_[0-9]*_filtered.csv files into three files each"""

    matching_files = [
        'jjhy_csv/core_csv_latest/jjhy_hanzi_parsed_3500_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_hanzi_parsed_5500_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_hanzi_parsed_6800_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_5000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_10000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_15000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_20000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_25000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_30000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_35000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_40000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_45000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_50000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_55000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_60000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_65000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_70000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_75000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_80000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_85000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_90000_filtered.csv',
        'jjhy_csv/core_csv_latest/jjhy_cihui_parsed_95000_filtered.csv',
        ]
    
    # if not matching_files:
    #     print(f"No files found matching pattern: {pattern}")
    #     exit()
    
    print(f"Found {len(matching_files)} files to process:")
    for file in matching_files:
        print(f"  - {file}")
    
    hsk_level_data = get_hsk_level_data()
    # Process each file separately
    for file_path in matching_files:
        print(f"\n{'='*60}")
        print(f"Processing file: {file_path}")
        print(f"{'='*60}")
        
        # Extract rank number from filename
        rank_match = re.search(r'/jjhy_(.*)_parsed_(\d+)_filtered\.csv', file_path)
        if rank_match:
            TAG = rank_match.group(1)
            rank_number = rank_match.group(2)
        else:
            print(f"Could not extract rank number from filename: {file_path}")
            continue
        
        print(f"Rank number: {rank_number}")
        
        # Read the source file
        df = pd.read_csv(file_path)
        
        print(f"Total rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
    
        separate_jjhy_csv(df,rank_number,TAG,hsk_level_data)

    print(f"\n{'='*60}")
    print(f"Processing complete! Processed {len(matching_files)} files.")
    print(f"{'='*60}")