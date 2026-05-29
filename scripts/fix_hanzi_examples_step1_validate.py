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

# Initialize OpenAI client with custom base URL for non-OpenAI model
url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
key = os.getenv('MODEL_API_KEY', 'not-needed')
model = os.getenv('MODEL_NAME', 'deepseek-r1')
print(f"base Url={url}\napi key={key}\nmodel name={model}")
client = OpenAI(
    base_url=url,
    api_key=key
)

def read_input_files():
    """Read the input CSV files."""
    print("正在读取输入文件...")
    # Read the main file that contains hanzi, pinyin, definition_cn, and example_cn
    main_df = pd.read_csv('others/all_hanzi_pinyin_definition_example.csv', dtype=str)
    return main_df

def clean_json_response(text):
    """Clean and prepare the JSON response for parsing."""
    # Remove markdown code block markers if present
    text = text.replace("```json", "").replace("```", "").strip()
    
    # Find the JSON array in the text
    match = re.search(r'\[[\s\S]*\]', text)
    if match:
        json_str = match.group(0)
        # Replace any unescaped quotes within the example strings
        json_str = re.sub(r'(?<!\\)"([^"]*?)(?<!\\)"', r'"\1"', json_str)
        return json_str
    return text

def validate_examples_batch(examples_batch):
    """Validate if example_cn matches the hanzi, pinyin, and definition_cn for a batch."""
    # Create a list of examples for the prompt
    examples_list = []
    for _, row in examples_batch.iterrows():
        examples_list.append({
            'id': row['definition_id'],
            'hanzi': row['hanzi'],
            'pinyin': row['pinyin'],
            'pos': row['pos'],
            'definition_cn': row['definition_cn'],
            'example_cn': row['example_cn']
        })
    
    prompt = f"""请验证以下例句是否与对应的汉字、拼音和释义匹配。对于每个例句。验证标准：
1. 例句必须包含指定的汉字
2. 汉字在例句中的读音必须与给定的拼音一致
3. 汉字在例句中的含义必须与给定的释义相符
4. 汉字在例句中的词性必须与给定的词性相符

例句列表：
{json.dumps(examples_list, ensure_ascii=False, indent=2)}

请按照以下JSON格式返回验证结果：
[
    {{
        "id": "123",
        "is_valid": true/false,
        "correct_example": "如果例句不符合以上标准，请直接提供符合标准的例句;否则返回空字符串"
    }},
    ...
]


要求：
1. 仅考虑以上4个标准，不要考虑其他因素，不要尝试微调例句。只要例句符合以上4个标准，就认为是正确的，否则提供符合标准的正确例句。
2. 必须使用JSON格式返回；。"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的中文语言验证助手，擅长验证中文例句的准确性和适用性。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        # Clean and prepare the JSON response
        result = clean_json_response(response.choices[0].message.content)
        
        try:
            validations = json.loads(result)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"有问题的JSON字符串: {result}")
            return {}
        
        # Create a mapping of definition_id to validation results
        validation_dict = {validation['id']: {
            'is_valid': validation['is_valid'],
            'correct_example': validation.get('correct_example', '')
        } for validation in validations}
        
        return validation_dict
    except Exception as e:
        print(f"验证例句时出错: {e}")
        return {}

def main():
    # Read input files
    main_df = read_input_files()
    
    # Process examples in batches
    batch_size = 50  # Process 50 examples at a time
    total_batches = (len(main_df) + batch_size - 1) // batch_size
    
    print(f"正在批量验证例句，每批{batch_size}个例句...")
    
    total_valid_count = 0
    total_invalid_count = 0
    
    for batch_idx in tqdm(range(271,total_batches)):
        batch_validation_results = []
        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, len(main_df))
        batch_df = main_df.iloc[start_idx:end_idx]
        
        # Validate examples for the batch
        validation_dict = validate_examples_batch(batch_df)
        
        # Add validation results to batch output data
        for _, row in batch_df.iterrows():
            def_id = row['definition_id']
            if def_id in validation_dict:
                validation = validation_dict[def_id]
                batch_validation_results.append({
                    'definition_id': def_id,
                    'hanzi': row['hanzi'],
                    'pinyin': row['pinyin'],
                    'pos': row['pos'],
                    'definition_cn': row['definition_cn'],
                    'example_cn': row['example_cn'],
                    'is_valid': validation['is_valid'],
                    'correct_example': validation['correct_example']
                })
                if validation['is_valid']:
                    total_valid_count += 1
                else:
                    total_invalid_count += 1
            else:
                # If validation failed, add with error status
                batch_validation_results.append({
                    'definition_id': def_id,
                    'hanzi': row['hanzi'],
                    'pinyin': row['pinyin'],
                    'pos': row['pos'],
                    'definition_cn': row['definition_cn'],
                    'example_cn': row['example_cn'],
                    'is_valid': False,
                    'correct_example': '请重新验证'
                })
                total_invalid_count += 1
        
        # Save batch results to a separate file
        if batch_validation_results:
            batch_output_df = pd.DataFrame(batch_validation_results)
            batch_output_file = f'others/hanzi_examples_validation_batch_{batch_idx:04d}.csv'
            batch_output_df.to_csv(batch_output_file, index=False, encoding='utf-8')
            print(f"批次 {batch_idx + 1} 验证结果已保存到 {batch_output_file}")
            
            # Print batch statistics
            batch_valid_count = sum(1 for result in batch_validation_results if result['is_valid'])
            batch_invalid_count = len(batch_validation_results) - batch_valid_count
            print(f"批次 {batch_idx + 1}: 验证 {len(batch_validation_results)} 个例句，有效 {batch_valid_count} 个，无效 {batch_invalid_count} 个")
        else:
            print(f"批次 {batch_idx + 1}: 没有生成任何验证结果")
        
        # Add a small delay between batches to avoid rate limiting
        time.sleep(1)
    
    # Print final summary statistics
    total_processed = total_valid_count + total_invalid_count
    if total_processed > 0:
        print(f"\n验证完成！总共验证 {total_processed} 个例句")
        print(f"有效例句: {total_valid_count} 个")
        print(f"无效例句: {total_invalid_count} 个")
        print(f"有效率: {total_valid_count/total_processed*100:.2f}%")
        print(f"所有批次文件已保存到 others/ 目录下")
    else:
        print("没有生成任何验证结果")

if __name__ == "__main__":
    main() 