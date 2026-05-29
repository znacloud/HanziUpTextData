#!/usr/bin/env python3
"""
Generate scene description prompts for each example sentence in a CSV file using a local Ollama model via Docker.

Reads 'database_csv/jjhy_core_hanzi_example.csv', extracts the first sentence from the 'example_cn' column (split by '|'), sends it to the Ollama LLM with the specified system and user prompts, and writes the results to new batch CSV files.
"""
from __future__ import annotations
import csv
import os
import time
from pathlib import Path
from typing import List, Dict
import requests

# optional progress bar
try:
    from tqdm import tqdm
except Exception:
    def tqdm(iterable, **kwargs):
        return iterable

INPUT_CSV = 'database_csv/jjhy_core_hanzi_example.csv'
OUTPUT_CSV = 'database_csv/jjhy_core_hanzi_example_scene_ollama.csv'
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/v1/chat/completions')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')

SYSTEM_PROMPT = """
你的任务是将输入的中文句子转换成一个“可被图像生成模型绘制的具体静态场景描述”。

要求：
1. 把抽象概念、性格、情绪、成语等内容转成可视化的动作、表情、物体或环境。
2. 输出必须是一个可以画出来的静态画面，包含人物、动作、表情、物体或场景特征。
3. 不要使用“这句话”“含义”“文本”等元语言词。
4. 不要添加原句中不存在的剧情或人物或变化过程。
5. 不要使用列表或分段，只输出一段自然语言描述。

示例：
输入：她是个碎嘴子。
输出：一个年轻女性不停地说话，表情生动，嘴巴快速张合，手势不断，比划个不停，显得特别健谈。

输入：井栏需要修缮。
输出：一口古老的石井，井栏破损、老化，出现裂缝和缺角，看起来急需修缮。

无论输入是什么，都只输出一个可视化的静态场景描述。
"""

USER_PROMPT_TEMPLATE = "请根据下面的内容生成一个可视化场景描述：\n{}"

def extract_first_example(example_field: str) -> str:
    if not example_field:
        return ''
    return example_field.split('｜')[0].strip()

def generate_scene_batch_ollama(sentences: List[str]) -> List[str]:
    if not sentences:
        return []
    user_prompt = USER_PROMPT_TEMPLATE.format('\n'.join(sentences))
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        out = data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        results = [ln.strip() for ln in out.splitlines() if ln.strip()]
        if len(results) < len(sentences):
            results += [''] * (len(sentences) - len(results))
        return results[:len(sentences)]
    except Exception as e:
        print(f"Ollama batch error: {e}")
        return [''] * len(sentences)

def main():
    input_path = Path(INPUT_CSV)
    output_path = Path(OUTPUT_CSV)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 1
    rows = []
    with input_path.open('r', encoding='utf-8-sig', newline='') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            example_id = row.get('example_id', '')
            example_field = row.get('example_cn', '')
            first_sentence = extract_first_example(example_field)
            if first_sentence and example_id:
                rows.append({'example_id': example_id, 'original_sentence': first_sentence})
    batch_size = 1
    save_interval = 100
    processed_rows = []
    save_idx = 0
    for batch_idx, i in enumerate(tqdm(range(0, len(rows), batch_size), desc='Ollama LLM batches')):
        batch = rows[i:i+batch_size]
        sentences = [r['original_sentence'] for r in batch]
        scene_results = generate_scene_batch_ollama(sentences)
        for j, scene in enumerate(scene_results):
            batch[j]['scene_description'] = scene
        processed_rows.extend(batch)
        # Save every 'save_interval' items
        if len(processed_rows) % save_interval == 0 or (i + batch_size) >= len(rows):
            save_idx += 1
            batch_output_path = output_path.with_name(f"{output_path.stem}_batch{save_idx}{output_path.suffix}")
            with batch_output_path.open('w', encoding='utf-8-sig', newline='') as f_out:
                fieldnames = ['example_id', 'original_sentence', 'scene_description']
                writer = csv.DictWriter(f_out, fieldnames=fieldnames)
                writer.writeheader()
                for row in processed_rows:
                    writer.writerow(row)
            processed_rows = []
    print(f"Scene descriptions written to {output_path.parent} as batch files.")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
