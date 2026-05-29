#!/usr/bin/env python3
"""
Generate scene description prompts for each example sentence in a CSV file using LLM.

Reads 'database_csv/jjhy_core_hanzi_exmaple.csv', extracts the first sentence from the 'example' column (split by '|'), sends it to the LLM with the specified system and user prompts, and writes the results to a new CSV file.
"""
from __future__ import annotations
import csv
import os
import time
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

# optional progress bar
try:
    from tqdm import tqdm
except Exception:
    def tqdm(iterable, **kwargs):
        return iterable

INPUT_CSV = 'database_csv/jjhy_core_hanzi_example.csv'
OUTPUT_CSV = 'database_csv/jjhy_core_hanzi_example_scene_llm.csv'

SYSTEM_PROMPT = (
    "你的任务是把每个中文句子转换成一个可被图像模型理解的“具体场景描述”。\n"
    "要求：\n"
    "1. 只描述句子本身的含义，不添加额外剧情。\n"
    "2. 把抽象概念转换成可视化的动作、表情、场景或物体。\n"
    "3. 输出必须简短、具体、可画出来。\n"
    "4. 不要出现“这句话”“含义”“文本”“句子”等词。\n"
    "5. 不要输出任何解释，只输出场景描述本身。"
)

USER_PROMPT_TEMPLATE = "请根据下面的内容生成一个可视化场景描述：\n{}"

# Load environment
load_dotenv()
URL = os.getenv('MODEL_API_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
KEY = os.getenv('MODEL_API_KEY', '')
MODEL = os.getenv('MODEL_NAME', 'qwen-turbo')

client = OpenAI(base_url=URL, api_key=KEY)

def extract_first_example(example_field: str) -> str:
    if not example_field:
        return ''
    return example_field.split('｜')[0].strip()

def generate_scene_batch(sentences: List[str]) -> List[str]:
    """Call the LLM for a batch of sentences, returns scene descriptions."""
    if not sentences:
        return []
    # Build user prompt: one sentence per line
    user_prompt = USER_PROMPT_TEMPLATE.format('\n'.join(sentences))
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            seed=1618,
            extra_body={"enable_thinking": False},
        )
        out = response.choices[0].message.content.strip()
        # Split output by lines, one scene per input
        results = [ln.strip() for ln in out.splitlines() if ln.strip()]
        # If not enough results, pad with ''
        if len(results) < len(sentences):
            results += [''] * (len(sentences) - len(results))
        return results[:len(sentences)]
    except Exception as e:
        print(f"LLM batch error: {e}")
        return [''] * len(sentences)

def main():
    input_path = Path(INPUT_CSV)
    output_path = Path(OUTPUT_CSV)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 1
    # Read all first sentences and example_id
    rows = []
    with input_path.open('r', encoding='utf-8-sig', newline='') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            example_id = row.get('example_id', '')
            example_field = row.get('example_cn', '')
            first_sentence = extract_first_example(example_field)
            if first_sentence and example_id:
                rows.append({'example_id': example_id, 'original_sentence': first_sentence})
    # Batch LLM calls
    batch_size = 10
    sleep_s = 0.2
    total_batches = (len(rows) + batch_size - 1) // batch_size
    for batch_idx, i in enumerate(tqdm(range(0, len(rows), batch_size), desc='LLM batches')):
        batch = rows[i:i+batch_size]
        sentences = [r['original_sentence'] for r in batch]
        scene_results = generate_scene_batch(sentences)
        for j, scene in enumerate(scene_results):
            batch[j]['scene_description'] = scene
        # Write this batch to a separate CSV file
        batch_output_path = output_path.with_name(f"{output_path.stem}_batch{batch_idx+1}{output_path.suffix}")
        with batch_output_path.open('w', encoding='utf-8-sig', newline='') as f_out:
            fieldnames = ['example_id', 'original_sentence', 'scene_description']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            for row in batch:
                writer.writerow(row)
        time.sleep(sleep_s)
    print(f"Scene descriptions written to {output_path.parent} as batch files.")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
