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
url = os.getenv('MODEL_API_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
key = os.getenv('MODEL_API_KEY', 'not-needed')
model = os.getenv('MODEL_NAME', 'deepseek-r1')
tag = os.getenv('MODEL_TAG', 'DS')
print(f"base Url={url}\napi key={key}\nmodel name={model}\ntag={tag}")
client = OpenAI(
    base_url=url,
    api_key=key
)

def read_input_files():
    print("正在读取输入文件...")
    main_df = pd.read_csv('others/hanzi_examples_extended_vs_generated.csv', dtype=str)
    return main_df

def clean_json_response(text):
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r'\[[\s\S]*\]', text)
    if match:
        json_str = match.group(0)
        json_str = re.sub(r'(?<!\\)"([^"\\]*?)(?<!\\)"', r'"\1"', json_str)
        return json_str
    return text

def select_better_example_batch(examples_batch):
    examples_list = []
    for _, row in examples_batch.iterrows():
        examples_list.append({
            'id': row['definition_id'],
            'hanzi': row['hanzi'],
            'pinyin': row['pinyin'],
            'pos': row['pos'],
            'definition_cn': row['definition_cn'],
            'example_1': row['extend_example_cn'],
            'example_2': row['generated_example_cn']
        })

    prompt = f"""例句列表：
{json.dumps(examples_list, ensure_ascii=False, indent=2)}

请根据以下标准，在每组 example_1 和 example_2 中选择更优的例句：
1. 例句必须包含指定的汉字
2. 汉字在例句中的读音必须与给定的拼音一致
3. 汉字在例句中的含义必须与给定的释义相符
4. 汉字在例句中的词性必须与给定的词性相符

请严格按照以下JSON格式返回每条数据的评判结果：
[
  {{
    "id": "xxx",
    "better": "1" 或 "2"
  }},
  ...
]

要求：
1. 仅考虑以上4个标准，不要考虑其他因素。
2. 必须使用JSON格式返回。
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的中文语言验证助手，擅长判断例句的优劣。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.01,
        )
        result = clean_json_response(response.choices[0].message.content)
        try:
            selections = json.loads(result)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"有问题的JSON字符串: {result}")
            return {}
        selection_dict = {sel['id']: sel for sel in selections}
        return selection_dict
    except Exception as e:
        print(f"选择更优例句时出错: {e}")
        return {}

def main():
    
    import time
    wait_seconds = 120*60  # You can adjust this value as needed
    for i in range(wait_seconds, 0, -60):
        print(f"等待 {i//60} 分钟后开始发送请求到 LLM...", end='\r', flush=True)
        time.sleep(60)
    print("\n开始发送请求到 LLM...")
    main_df = read_input_files()
    total_size = len(main_df)
    batch_size = 50  # LLM context limit, adjust as needed
    total_batches = (total_size + batch_size - 1) // batch_size
    print(f"正在批量评估例句，每批{batch_size}条...")
    # results = []
    for batch_idx in tqdm(range(25,total_batches)):
        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, total_size)
        batch_df = main_df.iloc[start_idx:end_idx]
        selection_dict = select_better_example_batch(batch_df)
        batch_results = []
        for _, row in batch_df.iterrows():
            def_id = row['definition_id']
            better = selection_dict.get(def_id, {}).get('better', '')
            batch_results.append({
                'definition_id': def_id,
                'hanzi': row['hanzi'],
                'pinyin': row['pinyin'],
                'pos': row['pos'],
                'definition_cn': row['definition_cn'],
                'example_1': row['extend_example_cn'],
                'example_2': row['generated_example_cn'],
                'better': better
            })
        # Save this batch to a separate file
        batch_output_file = f'others/hanzi_examples_better_selection_{tag}_batch_{batch_idx+1:04d}.csv'
        pd.DataFrame(batch_results).to_csv(batch_output_file, index=False, encoding='utf-8')
        print(f"批次 {batch_idx+1} 结果已保存到 {batch_output_file}")
        # results.extend(batch_results)
        # time.sleep(1)
    # out_df = pd.DataFrame(results)
    # out_df.to_csv('others/hanzi_examples_better_selection.csv', index=False, encoding='utf-8')
    # print('评估结果已保存到 others/hanzi_examples_better_selection.csv')

if __name__ == "__main__":
    main() 
