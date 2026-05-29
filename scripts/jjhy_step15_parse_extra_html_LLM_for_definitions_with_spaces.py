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
TAG = 'cihui'
# 0 when parse all, otherwise parse the first N rows
SAMPLE_SIZE = 0
# 0 when parse all, otherwise parse the first N files
SAMPLE_FLAG_SIZE = 0
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
JJHY HTML Parser - Simplified Version

This script parses HTML content from JJHY (现代汉语词典) and extracts vocabulary information.
Key features:
1. Processes each HTML individually
2. LLM returns one or more entries per HTML
3. Handles multiple entries per HTML automatically
4. Parses hanzi directly from HTML content

Output format: CSV with columns: rank, cihui, pinyin, ref_hanzi, ref_pinyin, pos, definition, example
"""

def read_input_files(file_path, invalid_parsed='', subdefs=''):
    print(f"正在读取输入文件...{file_path}")
    main_df = pd.read_csv(file_path, dtype=str)
    if invalid_parsed == 'True':
        main_df = main_df[main_df['invalid_parsed'] == 'True']
    elif invalid_parsed == 'False':
        main_df = main_df[main_df['invalid_parsed'] == 'False']

    if subdefs == 'True':
        main_df = main_df[main_df['has_subdefs'] == 'True']
    elif subdefs == 'False':
        main_df = main_df[main_df['has_subdefs'] == 'False']
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
            if line.strip().lower() in ['hanzi,pinyin,pos,definition,example', 'hanzi,pinyin,pos,definition,example,', 'hanzi,pinyin,pos,definition,example\n']:
                continue
            # Skip lines that are just the header
            if line.strip() == 'hanzi' or line.strip() == 'pinyin' or line.strip() == 'pos' or line.strip() == 'definition' or line.strip() == 'example':
                continue
            csv_lines.append(line.strip())
    return '\n'.join(csv_lines)

def parse_single_html(html_content, rank, cihui, original_pinyin):
    """Parse a single HTML content and return one or more entries"""
    prompt = f"""解析HTML提取词汇信息(汉字、拼音、词性、释义、例句),返回CSV格式：
hanzi,pinyin,pos,definition,example

HTML内容：
{html_content}

要求：
1. 从输入中提取以下字段：汉字(hanzi)、拼音(pinyin)、词性(pos)、释义(definition)、例句(example)
2. 完全去除所有HTML/XML标签，只保留纯文本内容
3. 注意：保持拼音、词性、释义和例句的原始内容绝对不变，不要增删字词，不要修改字词顺序！！！
4. 处理某条释义的例句时：
    - 如果某条释义没有例句，example字段设为空字符串""
    - 如果有多条例句，用"｜"符号连接它们
5. 忽略所有“用法说明"等非目标信息
6. 输出格式要求：
    - 每行一个完整条目
    - 字段顺序：hanzi,pinyin,pos,definition,example
    - 字段间用英文逗号分隔
    - 不包含任何表头或标题行

示例输出格式：
字,zì,名,文字,这是一个字｜请写个字
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个中文词汇解析助手，擅长从HTML提取汉字、拼音、词性、释义、例句，返回CSV格式。如果HTML中包含多个不同的汉字、拼音或释义，请为每个创建单独的行。只返回数据行，不要返回表头。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            seed=1618,
            extra_body={"enable_thinking": False}
        )
        result = clean_csv_response(response.choices[0].message.content)
        
        # Parse CSV response
        csv_lines = result.strip().split('\n')
        parsed_data = []
        sn_index = 0
        for line in csv_lines:
            if line.strip() and ',' in line:
                # Skip header rows
                if line.strip().lower() in ['hanzi,pinyin,pos,definition,example', 'hanzi,pinyin,pos,definition,example,']:
                    continue
                if line.strip() in ['hanzi', 'pinyin', 'pos', 'definition', 'example']:
                    continue
                
                parts = line.split(',', 4)  # Split into max 5 parts for hanzi,pinyin,pos,definition,example
                if len(parts) >= 5:
                    hanzi = parts[0].strip().strip('"')
                    pinyin = parts[1].strip().strip('"')
                    pos = parts[2].strip().strip('"')
                    definition = parts[3].strip().strip('"')
                    example = parts[4].strip().strip('"')
                    
                    # Skip if this looks like a header row
                    if hanzi.lower() == 'hanzi' or pinyin.lower() == 'pinyin':
                        continue
                    sn_index += 1
                    parsed_data.append({
                        'hanzi': hanzi,
                        'pinyin': pinyin,
                        'pos': pos,
                        'definition': definition,
                        'example': example,
                        'sn': sn_index
                    })
                elif len(parts) == 4:
                    hanzi = parts[0].strip().strip('"')
                    pinyin = parts[1].strip().strip('"')
                    pos = parts[2].strip().strip('"')
                    definition = parts[3].strip().strip('"')
                    
                    # Skip if this looks like a header row
                    if hanzi.lower() == 'hanzi' or pinyin.lower() == 'pinyin':
                        continue
                    sn_index += 1
                    parsed_data.append({
                        'hanzi': hanzi,
                        'pinyin': pinyin,
                        'pos': pos,
                        'definition': definition,
                        'example': '',
                        'sn': sn_index
                    })
                elif len(parts) == 3:
                    hanzi = parts[0].strip().strip('"')
                    pinyin = parts[1].strip().strip('"')
                    pos = parts[2].strip().strip('"')
                    
                    # Skip if this looks like a header row
                    if hanzi.lower() == 'hanzi' or pinyin.lower() == 'pinyin':
                        continue
                    sn_index += 1
                    parsed_data.append({
                        'hanzi': hanzi,
                        'pinyin': pinyin,
                        'pos': pos,
                        'definition': '',
                        'example': '',
                        'sn': sn_index
                    })
                elif len(parts) == 2:
                    hanzi = parts[0].strip().strip('"')
                    pinyin = parts[1].strip().strip('"')
                    
                    # Skip if this looks like a header row
                    if hanzi.lower() == 'hanzi' or pinyin.lower() == 'pinyin':
                        continue
                    sn_index += 1
                    parsed_data.append({
                        'hanzi': hanzi,
                        'pinyin': pinyin,
                        'pos': '',
                        'definition': '',
                        'example': '',
                        'sn': sn_index
                    })
                else:
                    hanzi = parts[0].strip().strip('"')
                    
                    # Skip if this looks like a header row
                    if hanzi.lower() == 'hanzi':
                        continue
                    sn_index += 1
                    parsed_data.append({
                        'hanzi': hanzi,
                        'pinyin': '',
                        'pos': '',
                        'definition': '',
                        'example': '',
                        'sn': sn_index
                    })
        
        # Create entries for each parsed item
        final_data = []
        for item in parsed_data:
            # Skip empty entries
            if not item.get('hanzi') and not item.get('pinyin') and not item.get('definition'):
                continue
                
            final_data.append({
                'rank': rank,
                f'{TAG}': item.get('hanzi', cihui),
                'pinyin': item.get('pinyin', original_pinyin),
                'ref_hanzi': '',
                'ref_pinyin': '',
                'pos': item.get('pos', ''),
                'definition': item.get('definition', ''),
                'example': item.get('example', ''),
                'sn': item.get('sn', '')
            })
        
        return final_data
    except Exception as e:
        print(f"解析HTML时出错: {e}")
        # Return fallback entry
        return [{
            'rank': rank,
            f'{TAG}': cihui,
            'pinyin': original_pinyin,
            'ref_hanzi': '',
            'ref_pinyin': '',
            'pos': '',
            'definition': '',
            'example': '',
            'sn': ''
        }]

def main(file_path, flag_num):
    print(f"开始解析HTML内容...{file_path}, flag_num={flag_num}, sample_size={SAMPLE_SIZE}")
    main_df = read_input_files(file_path)
    main_df = main_df[:SAMPLE_SIZE] if SAMPLE_SIZE > 0 else main_df
    main_df = main_df.reset_index(drop=True)
    total_size = len(main_df)
    print(f"总共需要解析 {total_size} 条记录...")
    
    all_results = []
    
    for idx, row in tqdm(main_df.iterrows(), total=total_size):
        # Parse each HTML individually
        parsed_data = parse_single_html(
            row['raw_html'], 
            row['rank'], 
            row[f'{TAG}'], 
            row['pinyin']
        )
        
        if parsed_data:
            all_results.extend(parsed_data)
        else:
            # red color
            print(f"\033[91m没有成功解析数据: {row['rank']}, {row[f'{TAG}']}, {row['pinyin']}\033[0m")
        
        # Save progress every 100 records
        print(f"idx={idx}, total_size={total_size}")
        if (idx + 1) % 100 == 0 or idx == total_size - 1:
            temp_df = pd.DataFrame(all_results)
            all_results = []
            if not temp_df.empty:
                columns_order = ['rank','sn', f'{TAG}', 'pinyin', 'ref_hanzi', 'ref_pinyin', 'pos', 'definition', 'example']
                temp_df = temp_df.reindex(columns=columns_order, fill_value='')
                file_name = f'jjhy_csv/llm_parsed_csv/jjhy_{TAG}_fixdefinition_parsed_{flag_num}_{idx+1}.csv'
                temp_df.to_csv(file_name, index=False, encoding='utf-8')
                print(f"已保存进度到 {file_name}")
            else:
                # red color
                print(f"\033[91m没有成功解析任何数据\033[0m")
        
        # Add delay to avoid rate limiting
        # time.sleep(1)
    
    # # Save all results to final file
    # if all_results:
    #     final_df = pd.DataFrame(all_results)
    #     # Ensure columns are in the correct order
    #     columns_order = ['rank', f'{TAG}', 'pinyin', 'ref_hanzi', 'ref_pinyin', 'pos', 'definition', 'example']
    #     final_df = final_df.reindex(columns=columns_order, fill_value='')
    #     final_output_file = f'others/jjhy_{TAG}_parsed_final.csv'
    #     final_df.to_csv(final_output_file, index=False, encoding='utf-8')
    #     print(f'所有解析结果已保存到 {final_output_file}')
    #     print(f'总共解析了 {len(all_results)} 条记录')
        
    #     # Print some statistics
    #     unique_hanzi = final_df[f'{TAG}'].nunique()
    #     unique_pinyin = final_df['pinyin'].nunique()
    #     print(f'唯一汉字数量: {unique_hanzi}')
    #     print(f'唯一拼音数量: {unique_pinyin}')
    # else:
    #     print("没有成功解析任何数据")

if __name__ == "__main__":

    # arg_parser = argparser.pa
    # wait for 2 hour
    # print("wait for 2.5 hour...")
    # time.sleep(3600*2.5)

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
    for flag_num in flag_nums:
        file_path = f'jjhy_csv/tofixdefinition/jjhy_{TAG}_html_{flag_num}.csv'
        main(file_path, flag_num) 
