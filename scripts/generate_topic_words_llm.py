#!/usr/bin/env python3
"""Generate hanzi/words for each topic using LLM.

Reads topics from raw_data/hanzi_topic.csv, queries the LLM to generate words/characters
for each topic, and writes the results to a CSV file with columns: id, topic, hanzi.

Usage:
  python scripts/generate_topic_words_llm.py [--output <output_file>] [--start-id <id>] [--dry-run]

This follows the OpenAI-compatible client usage in `generate_examples_llm.py`.
"""
from __future__ import annotations

import argparse
import csv
import os
import time
from pathlib import Path
from typing import List, Dict, Tuple

from dotenv import load_dotenv
from openai import OpenAI

# optional progress bar (shows ETA). If not installed, fall back to a no-op iterator.
try:
    from tqdm import tqdm
except Exception:
    def tqdm(iterable, **kwargs):
        return iterable

# Load environment
load_dotenv()
URL = os.getenv('MODEL_API_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
KEY = os.getenv('MODEL_API_KEY', '')
MODEL = os.getenv('MODEL_NAME', 'qwen-turbo-latest')

client = OpenAI(base_url=URL, api_key=KEY)


def read_topics(csv_file: Path) -> List[Dict[str, str]]:
    """Read topics from hanzi_topic.csv.
    
    Returns a list of dicts with keys: id, topic, category
    """
    topics = []
    with csv_file.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            topics.append(row)
    return topics


def generate_words_for_topic(topic: str, start_id: int, count_min: int = 200, count_max: int = 400) -> Tuple[List[str], int]:
    """Call the LLM to generate words for a specific topic.
    
    Args:
        topic: The topic name (e.g., "动物")
        start_id: Starting ID for the first generated word
        count_min: Minimum number of words to generate
        count_max: Maximum number of words to generate
    
    Returns:
        (list of words, next_id) where next_id is start_id + number of words generated
    """
    prompt = (
        f"你是汉语言专家，擅长汉语学习指导，现在我要制定一个以\"{topic}\"为主题的字词列表，"
        f"请以\"id,topic,hanzi\"的csv格式列出所有可能的该类主题的字词。"
        f"id从{start_id}开始递增，topic都是\"{topic}\"。"
        f"要尽量包含所有相关词语,数量在{count_min}到{count_max}之间。"
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个中文专家，擅长生成与特定主题相关的汉字和词汇列表。"
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            temperature=0.7,
            seed=1618,
            extra_body={"enable_thinking": False},
        )
        
        out = response.choices[0].message.content.strip()
        
        # Strip possible fences and normalize
        if out.startswith('```') and out.endswith('```'):
            out = out.strip('`').strip()
        if out.startswith('```csv'):
            out = out[6:].strip('`').strip()
        out = out.replace('\r', '').strip()
        
        # Parse CSV output: expect lines like "id,topic,hanzi"
        words = []
        current_id = start_id
        
        for line in out.splitlines():
            line = line.strip()
            if not line or line.lower().startswith('id,'):
                # Skip header or empty lines
                continue
            
            # Try to parse the CSV line
            parts = line.split(',')
            if len(parts) >= 3:
                # Extract the hanzi (word) part - it's the last part
                hanzi = parts[-1].strip().strip('"').strip()
                if hanzi and hanzi != 'hanzi':  # Skip if empty or if it's a header
                    words.append(hanzi)
                    current_id += 1
            elif len(parts) == 1:
                # If there's only one part, treat it as a hanzi
                hanzi = parts[0].strip().strip('"').strip()
                if hanzi and hanzi not in ['id', 'hanzi', 'topic']:
                    words.append(hanzi)
                    current_id += 1
        
        return words, current_id
    
    except Exception as e:
        print(f"LLM error for topic '{topic}': {e}")
        return [], start_id


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate words for each topic using LLM')
    parser.add_argument('--output', required=False, default='jjhy_csv/topic/hanzi_topic_words.csv',
                        help='Output CSV file path')
    parser.add_argument('--start-id', type=int, required=False, default=8018,
                        help='Starting ID for generated words (default: 8018)')
    parser.add_argument('--topics-file', required=False, default='raw_data/hanzi_topic.csv',
                        help='Input CSV file with topics')
    parser.add_argument('--dry-run', action='store_true', help='Do not write files; only print counts and samples')
    parser.add_argument('--sleep', type=float, default=0.5, help='Seconds to sleep between LLM calls (rate limit)')
    parser.add_argument('--skip-category', required=False, help='Skip topics with this category (e.g., "场景" or "功能")')
    args = parser.parse_args()

    topics_file = Path(args.topics_file)
    output_file = Path(args.output)

    if not topics_file.exists():
        print(f"Topics file does not exist: {topics_file}")
        return 2

    # Read topics
    topics = read_topics(topics_file)
    print(f"Loaded {len(topics)} topics from {topics_file}")

    # Filter topics if skip_category is specified
    if args.skip_category:
        topics = [t for t in topics if t.get('category', '') != args.skip_category]
        print(f"After filtering: {len(topics)} topics")

    # Generate words for each topic
    current_id = args.start_id
    all_rows: List[Tuple[int, str, str]] = []

    for topic_row in tqdm(topics, desc='Processing topics'):
        topic_name = topic_row['topic']
        print(f"\nGenerating words for topic: {topic_name}")

        words, current_id = generate_words_for_topic(topic_name, current_id)
        
        for word in words:
            all_rows.append((current_id - len(words) + words.index(word), topic_name, word))

        print(f"  Generated {len(words)} words (IDs: {current_id - len(words)}-{current_id - 1})")

        # Rate limit between topics
        time.sleep(args.sleep)

    # Recalculate IDs to ensure they're sequential
    all_rows_fixed = []
    current_id = args.start_id
    for _, topic_name, word in all_rows:
        all_rows_fixed.append((current_id, topic_name, word))
        current_id += 1

    print(f"\n{'='*60}")
    print(f"Summary: Generated {len(all_rows_fixed)} words total")
    print(f"ID range: {args.start_id} - {args.start_id + len(all_rows_fixed) - 1}")
    
    if not args.dry_run:
        # Write output CSV
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'topic', 'hanzi'])
            for row_id, topic_name, word in all_rows_fixed:
                writer.writerow([row_id, topic_name, word])
        
        print(f"Wrote results to: {output_file}")
    else:
        print("(dry-run mode: no files written)")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
