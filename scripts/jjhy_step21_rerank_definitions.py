import pandas as pd
from openai import OpenAI
from tqdm import tqdm
import os
from dotenv import load_dotenv
import time
import json
import re

# Load environment variables
load_dotenv()
TAG = 'cihui'  # or 'hanzi' depending on the file type
# True when only process those with multiple definitions
MULTIPLE_DEFS = True
# 0 when process all, otherwise process the first N rows
SAMPLE_SIZE = 0
# 0 when process all, otherwise process the first N files
SAMPLE_FLAG_SIZE = 0
# Number of rank groups to process in a single LLM call (larger = faster but may hit token limits)
BATCH_SIZE = 1
# Initialize OpenAI client with custom base URL for non-OpenAI model
url = os.getenv('MODEL_API_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
key = os.getenv('MODEL_API_KEY', 'not-needed')
model = os.getenv('MODEL_NAME', 'qwen-turbo-latest')
print(f"base Url={url}\napi key={key}\nmodel name={model}")
client = OpenAI(
    base_url=url,
    api_key=key
)

"""
JJHY Definition Reranking Script

This script reranks definitions for the same hanzi/cihui based on frequency and usage patterns.
Key features:
1. Processes each CSV file in jjhy_csv/core_csv_rank_duplicates/
2. Groups definitions by rank (same hanzi/cihui)
3. Uses LLM to rerank definitions based on frequency (daily > professional, general > specific, active > passive)
4. Processes multiple rank groups in batches for improved speed
5. Outputs complete data with all original columns plus new_sn for reranking

Output format: Complete CSV with all original columns plus new_sn column
"""

def read_input_files(file_path):
    print(f"正在读取输入文件...{file_path}")
    main_df = pd.read_csv(file_path, dtype=str)
    
    # Convert all columns to string type to handle NaN values
    for col in main_df.columns:
        main_df[col] = main_df[col].astype(str).replace('nan', '')
    
    # if MULTIPLE_DEFS:
    #     # Only process rows that have multiple definitions for the same rank
    #     rank_counts = main_df['rank'].value_counts()
    #     multiple_def_ranks = rank_counts[rank_counts > 1].index
    #     main_df = main_df[main_df['rank'].isin(multiple_def_ranks)]
    
    return main_df

def clean_csv_response(text):
    """Clean and extract CSV from LLM response"""
    text = text.replace("```csv", "").replace("```", "").strip()
    # Find CSV content (lines with commas)
    lines = text.strip().split('\n')
    csv_lines = []
    for line in lines:
        if ',' in line and line.strip():
            # Skip header rows
            if line.strip().lower() in ['rank,new_sn,sn', 'rank,new_sn,sn,', 'rank,new_sn,sn\n']:
                continue
            # Skip lines that are just the header
            if line.strip() == 'rank' or line.strip() == 'new_sn' or line.strip() == 'sn':
                continue
            csv_lines.append(line.strip())
    return '\n'.join(csv_lines)

def rerank_definitions_batch(rank_groups, batch_size=5):
    """Rerank definitions for multiple rank groups in a single LLM call"""
    all_reranked_data = []
    
    # Calculate total batches for progress bar
    total_batches = (len(rank_groups) + batch_size - 1) // batch_size
    
    # Process rank groups in batches with progress bar
    for i in tqdm(range(0, len(rank_groups), batch_size), 
                  total=total_batches, 
                  desc="Processing batches", 
                  unit="batch"):
        batch = rank_groups[i:i + batch_size]
        
        # Prepare batch data for LLM
        batch_input = []
        for rank, group_df in batch:
            cihui = group_df.iloc[0][TAG]
            for _, row in group_df.iterrows():
                # print(row)
                batch_input.append({
                    'id': rank,
                    'sn': str(row['sn']),
                    'cihui': str(cihui),
                    'pinyin': str(row['pinyin']),
                    'pos': str(row['pos']),
                    'definition': str(row['definition']),
                    'example': str(row['example']).split('|')[0] if pd.notna(row['example']) and str(row['example']).lower() != 'nan' else ''
                })
        
        # Create prompt for batch processing
        prompt = f"""下面的CSV内容的每一行代表字词的一条释义及其例句（搭配），sn是当前释义的排序。现在需要对字词的释义重新排序，请根据该字词的拼音、词性以及释义的常见情况对释义重新排序，最常用的释义排第一，依次类推：
id,zici,pinyin,sn,pos,definition,example
"""
        
        for item in batch_input:
            prompt += f"{item['id']},{item['cihui']},{item['pinyin']},{item['sn']},{item['pos']},\"{item['definition']}\",\"{item['example']}\"\n"
        
        prompt += f"""

============
将排序后的结果以如下csv格式输出,id是字词的唯一标识，origin_sn是当前释义的序号，new_sn是重新排序后的序号：
id,origin_sn,new_sn
"""
        
        # # Add example output for first few items
        # for rank, group_df in batch[:2]:  # Show example for first 2 groups
        #     group_size = len(group_df)
        #     for j in range(1, group_size + 1):
        #         prompt += f"{rank},{j},{group_size - j + 1}\n"
        

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    # {"role": "system", "content": "你是一个中文词汇排序助手，擅长根据使用频率和日常性对中文释义进行重新排序。只返回CSV格式的排序结果，不要其他解释。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                seed=1618,
                extra_body={"enable_thinking": False}
            )
            result = clean_csv_response(response.choices[0].message.content)
            
            # Parse CSV response
            csv_lines = result.strip().split('\n')
            batch_reranked_data = []
            
            for line in csv_lines:
                if line.strip() and ',' in line:
                    # Skip header rows
                    if line.strip().lower() in ['id,origin_sn,new_sn', 'id,origin_sn,new_sn,']:
                        continue
                    if line.strip() in ['id', 'origin_sn', 'new_sn']:
                        continue
                    
                    parts = line.split(',', 2)  # Split into max 3 parts for id,origin_sn,new_sn
                    if len(parts) >= 3:
                        id_val = parts[0].strip().strip('"')
                        origin_sn = parts[1].strip().strip('"')
                        new_sn = parts[2].strip().strip('"')
                        
                        # Skip if this looks like a header row
                        if id_val.lower() == 'id' or new_sn.lower() == 'new_sn':
                            continue
                        
                        batch_reranked_data.append({
                            'rank': id_val,
                            'origin_sn': origin_sn,
                            'new_sn': new_sn
                        })
            
            all_reranked_data.extend(batch_reranked_data)
            print(f"成功处理批次 {i//batch_size + 1}/{(len(rank_groups) + batch_size - 1)//batch_size}")
            
        except Exception as e:
            print(f"批次处理时出错 (批次 {i//batch_size + 1}): {e}")
            # Return fallback ranking for this batch (keep original order)
            for rank, group_df in batch:
                for i, (_, row) in enumerate(group_df.iterrows(), 1):
                    all_reranked_data.append({
                        'rank': rank,
                        'origin_sn': row['sn'],
                        'new_sn': '-1'
                    })
        
        # Add delay between batches to avoid rate limiting
        if i + batch_size < len(rank_groups):
            time.sleep(1)
    
    return all_reranked_data

def main(file_path, flag_num):
    print(f"开始重新排序定义...{file_path}, flag_num={flag_num}, sample_size={SAMPLE_SIZE}, multiple_defs={MULTIPLE_DEFS}")
    main_df = read_input_files(file_path)
    main_df = main_df[:SAMPLE_SIZE] if SAMPLE_SIZE > 0 else main_df
    main_df = main_df.reset_index(drop=True)
    total_size = len(main_df)
    print(f"总共需要处理 {total_size} 条记录...")
    
    # Group by rank to process definitions together
    grouped = main_df.groupby('rank')
    total_groups = len(grouped)
    print(f"总共需要处理 {total_groups} 个词汇组...")
    
    all_results = []
    
    # Convert grouped data to list of tuples for batch processing
    print("准备批量处理数据...")
    rank_groups_list = [(rank, group_df) for rank, group_df in grouped if len(group_df) > 1]
    
    if rank_groups_list:
        print(f"开始批量处理 {len(rank_groups_list)} 个多定义词汇组...")
        all_results = rerank_definitions_batch(rank_groups_list, batch_size=BATCH_SIZE)
    else:
        print("没有找到多定义的词汇组")
        all_results = []
    
    # Save all results to final file
    if all_results:
        print("正在合并重新排序结果...")
        
        # Create reranking mapping DataFrame
        rerank_df = pd.DataFrame(all_results)
        
        # Merge with original data to get all columns
        # First, create a mapping from (rank, sn) to new_sn
        rerank_mapping = rerank_df.set_index(['rank', 'origin_sn'])['new_sn'].to_dict()
        
        # Add new_sn column to original data
        print("正在添加新序号列...")
        main_df['new_sn'] = main_df.apply(
            lambda row: rerank_mapping.get((row['rank'], row['sn']), '-2'), 
            axis=1
        )

        
        # Reorder rows based on new_sn within each rank group
        print("正在重新排序数据...")
        main_df = main_df.sort_values(['rank', 'new_sn']).reset_index(drop=True)
        
        # Ensure output directory exists
        output_dir = f'jjhy_csv/reranked_definitions'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the complete reranked data with all original columns
        print("正在保存完整重新排序数据...")
        final_output_file = f'{output_dir}/reranked_{TAG}_{flag_num}_final.csv'
        main_df.to_csv(final_output_file, index=False, encoding='utf-8')
        print(f'所有重新排序结果已保存到 {final_output_file}')
        print(f'总共重新排序了 {len(all_results)} 条记录')
        
        # Print some statistics
        unique_ranks = main_df['rank'].nunique()
        print(f'唯一词汇数量: {unique_ranks}')
        
        # Also save the reranking mapping separately for reference
        print("正在保存重新排序映射...")
        mapping_file = f'{output_dir}/reranking_mapping_{TAG}_{flag_num}.csv'
        rerank_df.to_csv(mapping_file, index=False, encoding='utf-8')
        print(f'重新排序映射已保存到 {mapping_file}')
    else:
        print("没有成功重新排序任何数据")

if __name__ == "__main__":
    # wait for 2 hour
    # print("wait for 2 hour...")
    # time.sleep(3600*2)
    # Process all files in the core_csv_rank_duplicates directory
    cihui_nums = ['5000', 
                   '10000',
                   '15000',
                   '20000',
                   '25000',
                   '30000',
                   '35000',
                   '40000',
                   '45000',
                   '50000',
                   '55000',
                   '60000',
                   '65000',
                   '70000',
                   '75000',
                   '80000',
                   '85000',
                   '90000',
                   '95000',
                   ]
    hanzi_nums = ['3500',
                   '5500',
                   '6800',
                  ]
    flag_nums = cihui_nums if TAG == 'cihui' else hanzi_nums
    flag_nums = flag_nums[:SAMPLE_FLAG_SIZE] if SAMPLE_FLAG_SIZE > 0 else flag_nums
    
    print(f"开始处理 {len(flag_nums)} 个文件...")
    for flag_num in tqdm(flag_nums, desc="Processing files", unit="file"):
        file_path = f'jjhy_csv/core_csv_rank_duplicates/jjhy_{TAG}_parsed_{flag_num}_filtered.csv'
        if os.path.exists(file_path):
            main(file_path, flag_num)
        else:
            print(f"文件不存在: {file_path}")
