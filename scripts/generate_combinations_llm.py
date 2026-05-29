#!/usr/bin/env python3
"""Generate hanzi combinations (字词常见搭配) for each hanzi in jjhy_core_hanzi.csv.

Reads the jjhy_core_hanzi.csv file, queries the LLM to generate 3 common word
combinations for each hanzi, and writes the results to a new CSV file with
a 'combinations' column.

Usage:
  python scripts/generate_combinations_llm.py --src <src_file> --dst <dst_file> [--dry-run]

This follows the OpenAI-compatible client usage in `generate_examples_llm.py`.
"""
from __future__ import annotations

import argparse
import csv
import os
import time
from pathlib import Path
from typing import List, Dict

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


def generate_combinations_batch(items: List[Dict[str, str]], num_combinations: int = 3) -> List[str]:
    """Call the LLM once for a batch of hanzi items.

    items: list of dicts with keys: hanzi_id, hanzi
    Returns a list of combination strings ('' if none) in the same order as items.
    Each combination string contains up to 3 word combinations separated by '｜'.
    """
    if not items:
        return []

    # Build a numbered prompt so the model returns results in order.
    lines = [
        f"{i+1}) 汉字：{it['hanzi']}"
        for i, it in enumerate(items)
    ]

    prompt = (
        "请为下面按序号列出的汉字分别生成 " + str(num_combinations) + " 个常见的字词搭配。\n\n"
        + "每行输入格式：序号) 汉字：...\n\n"
        + "要求：\n"
        + "1) 只返回按序号对应的字词搭配，每行对应一个汉字的结果；多个搭配请用竖线字符 `｜` 连接（例如：搭配1｜搭配2｜搭配3）。\n"
        + "2) 行的开头必须保留序号和一个分隔符 '|||' 用来将输入和输出分开，例如：1|||搭配1｜搭配2｜搭配3\n"
        + "3) 每个搭配必须包含给定的汉字，且保持汉字原形不变。\n"
        + "4) 字词搭配应该是 2-10 个汉字组成的常用词语或短语，越常用越好。\n"
        + "5) 优先选择高频词汇，避免生僻或专业术语。\n"
        + "6) 如果无法生成合适搭配，请仅返回序号和分隔符，分隔符后留空（例如：2|||\n）。\n\n"
        + "输入：\n"
        + "\n".join(lines)
        + "\n\n请严格按照格式输出，每行一条，形如：序号|||搭配1｜搭配2｜搭配3 或 序号|||（留空）。\n"
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个中文字词搭配生成器，擅长根据给定的汉字生成常见的字词搭配。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            seed=1618,
            extra_body={"enable_thinking": False},
        )
        out = response.choices[0].message.content.strip()
        # Strip possible fences and normalize
        if out.startswith('```') and out.endswith('```'):
            out = out.strip('`').strip()
        out = out.replace('\r', '').strip()

        # Parse lines: expect lines like '1|||搭配1｜搭配2｜搭配3' or '2|||' for empty
        results: List[str] = [''] * len(items)
        for line in out.splitlines():
            if '|||' in line:
                left, right = line.split('|||', 1)
                # try to extract index from left (may be like '1)' or '1')
                idx_part = ''.join(ch for ch in left if ch.isdigit())
                if not idx_part:
                    continue
                idx = int(idx_part) - 1
                if 0 <= idx < len(items):
                    results[idx] = right.strip()

        # Fallback: if parsing failed and there's exactly as many non-empty newline parts as items,
        # assign them in order
        non_empty = [ln.strip() for ln in out.splitlines() if ln.strip()]
        if all('|||' not in ln for ln in non_empty) and len(non_empty) == len(items):
            results = non_empty

        return results
    except Exception as e:
        print(f"LLM batch error: {e}")
        return [''] * len(items)


def process_file(src: Path, dst: Path | None, dry_run: bool = False, sleep_s: float = 0.2, batch_size: int = 20) -> tuple[int, int, list[str]]:
    """Process the CSV file, generate combinations for each hanzi.

    Returns (rows_seen, rows_updated, samples) where samples are up to 5 generated combination strings for reporting.
    """
    rows_seen = 0
    rows_updated = 0
    samples: list[str] = []

    with src.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return 0, 0, []

        # Verify required columns
        try:
            hanzi_id_idx = header.index('hanzi_id')
            hanzi_idx = header.index('hanzi')
        except ValueError as e:
            raise RuntimeError(f"Required column missing in {src}: {e}")

        # Add combinations column if not present
        if 'combinations' in header:
            comb_idx = header.index('combinations')
        else:
            header.append('combinations')
            comb_idx = len(header) - 1

        rows: list[list[str]] = [r for r in reader]
        # ensure every row has correct length
        for i, row in enumerate(rows):
            if len(row) < len(header):
                rows[i] = row + [''] * (len(header) - len(row))

        rows_seen = len(rows)

        # Collect indices that need combinations (all rows in this case)
        to_fill: List[int] = []
        for i, row in enumerate(rows):
            comb_val = row[comb_idx].strip() if comb_idx < len(row) else ''
            if not comb_val:
                to_fill.append(i)

        # In dry-run mode, only actually call the LLM for the first batch
        sample_batches_to_call = 1 if dry_run else None
        batches = [to_fill[i : i + batch_size] for i in range(0, len(to_fill), batch_size)]
        total_batches = len(batches)

        for b_idx, batch in enumerate(tqdm(batches, desc=f'batches for {src.name}', leave=False)):
            if not batch:
                continue

            # prepare items for LLM
            items = []
            for row_idx in batch:
                row = rows[row_idx]
                items.append({
                    'hanzi_id': row[hanzi_id_idx].strip() if hanzi_id_idx < len(row) else '',
                    'hanzi': row[hanzi_idx].strip() if hanzi_idx < len(row) else '',
                })

            # Decide whether to call LLM for this batch
            call_llm = True
            if dry_run and sample_batches_to_call is not None and b_idx >= sample_batches_to_call:
                call_llm = False

            generated_list: List[str]
            if call_llm:
                generated_list = generate_combinations_batch(items)
            else:
                generated_list = [''] * len(items)

            # assign back
            for idx_in_batch, row_idx in enumerate(batch):
                gen = generated_list[idx_in_batch].strip() if idx_in_batch < len(generated_list) else ''
                if gen:
                    rows[row_idx][comb_idx] = gen
                    rows_updated += 1
                    if len(samples) < 5:
                        samples.append(f"{rows[row_idx][hanzi_idx]} -> {gen}")

            # rate limit
            time.sleep(sleep_s)

            # progress for this file: print batch progress inline
            try:
                pct = (b_idx + 1) / total_batches * 100 if total_batches > 0 else 100
                print(f"Processing {src.name}: batch {b_idx+1}/{total_batches} ({pct:.0f}%)\r", end='', flush=True)
            except Exception:
                pass

            # Save incremental batch results to batch-suffixed file
            if not dry_run and dst is not None:
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    base = dst.stem
                    suff = f".batch{b_idx+1}.csv"
                    batch_file = dst.with_name(base + suff)
                    with batch_file.open('w', encoding='utf-8-sig', newline='') as out_f:
                        writer = csv.writer(out_f)
                        writer.writerow(header)
                        # Write only the rows in the current batch with their updates
                        writer.writerows([rows[row_idx] for row_idx in batch])
                except Exception as e:
                    print(f"Warning: failed to write batch results for {dst}: {e}")

    # Write final complete output file
    if not dry_run and dst is not None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open('w', encoding='utf-8-sig', newline='') as out_f:
            writer = csv.writer(out_f)
            writer.writerow(header)
            writer.writerows(rows)

    return rows_seen, rows_updated, samples


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate hanzi combinations (字词常见搭配) using LLM')
    parser.add_argument('--src', required=False, default='jjhy_csv/core_csv_latest/jjhy_core_hanzi.csv', help='Source CSV file')
    parser.add_argument('--dst', required=False, default='jjhy_csv/core_csv_with_combinations/jjhy_core_hanzi_combinations.csv', help='Destination CSV file')
    parser.add_argument('--dry-run', action='store_true', help='Do not write files; only print counts and samples')
    parser.add_argument('--sleep', type=float, default=0.25, help='Seconds to sleep between LLM calls (rate limit)')
    parser.add_argument('--batch-size', type=int, default=20, help='Number of hanzi to send to LLM in one batch')
    args = parser.parse_args()

    src_file = Path(args.src)
    dst_file = Path(args.dst)

    if not src_file.exists() or not src_file.is_file():
        print(f"Source file does not exist: {src_file}")
        return 2

    print(f"Processing file: {src_file}")
    print(f"Output will be saved to: {dst_file}")
    print(f"Batch size: {args.batch_size}")
    print(f"Sleep between batches: {args.sleep}s")
    if args.dry_run:
        print("DRY RUN MODE - only first batch will be processed")
    print()

    seen, updated, samples = process_file(
        src_file, 
        dst_file if not args.dry_run else None, 
        dry_run=args.dry_run, 
        sleep_s=args.sleep, 
        batch_size=args.batch_size
    )

    print(f"\n\nSummary:")
    print(f"  Total hanzi processed: {seen}")
    print(f"  Hanzi with combinations generated: {updated}")
    
    if samples:
        print("\nSample generated combinations:")
        for s in samples:
            print(f"  - {s}")

    if not args.dry_run:
        print(f"\n✓ Results saved to: {dst_file}")
    else:
        print("\n(Dry run completed - no files written)")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
