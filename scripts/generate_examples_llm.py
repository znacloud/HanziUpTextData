#!/usr/bin/env python3
"""Generate example sentences for CSV rows that have empty 'example' field.

Reads CSV files from a source directory (default: jjhy_csv/core_csv_no_exmaples/),
finds rows whose example column is empty, queries the LLM to generate one or two
example sentences, and writes updated CSV files to a destination directory
preserving the original filenames.

Usage:
  python scripts/generate_examples_llm.py --src <src_dir> --dst <dst_dir> [--dry-run]

This follows the OpenAI-compatible client usage in `jjhy_step8_parse_html_LLM.py`.
"""
from __future__ import annotations

import argparse
import csv
import os
import time
from pathlib import Path
from typing import Iterable, List, Dict

from dotenv import load_dotenv
from openai import OpenAI

# optional progress bar (shows ETA). If not installed, fall back to a no-op iterator.
try:
    from tqdm import tqdm
except Exception:
    def tqdm(iterable, **kwargs):
        return iterable

TAG = 'cihui'
# Load environment
load_dotenv()
URL = os.getenv('MODEL_API_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
KEY = os.getenv('MODEL_API_KEY', '')
MODEL = os.getenv('MODEL_NAME', 'qwen-turbo-latest')

client = OpenAI(base_url=URL, api_key=KEY)


def find_csv_files(src_dir: Path) -> Iterable[Path]:
    for p in sorted(src_dir.iterdir()):
        if p.is_file() and p.suffix.lower() == ".csv" and p.name.startswith(f'jjhy_{TAG}_'):
            yield p


def detect_column_index(header: list[str], candidates: tuple[str, ...]) -> int | None:
    lower = [h.strip().lower() for h in header]
    for name in candidates:
        if name in lower:
            return lower.index(name)
    # fallback: substring match
    for i, h in enumerate(lower):
        for name in candidates:
            if name in h:
                return i
    return None


def generate_examples_batch(items: List[Dict[str, str]], max_examples: int = 2) -> List[str]:
    """Call the LLM once for a batch of items.

    items: list of dicts with keys: word, pinyin, pos, definition
    Returns a list of example strings ('' if none) in the same order as items.
    """
    if not items:
        return []

    # Build a numbered prompt so the model returns results in order.
    lines = [
        f"{i+1}) 词：{it['word']} | 拼音：{it.get('pinyin','')} | 词性：{it.get('pos','')} | 释义：{it.get('definition','')}"
        for i, it in enumerate(items)
    ]

    prompt = (
        "请为下面按序号列出的词条分别生成最多 " + str(max_examples) + " 条中文例句。\n\n"
        + "每行输入格式：序号) 词：... | 拼音：... | 词性：... | 释义：...\n\n"
        + "要求：\n"
        + "1) 只返回按序号对应的例句，每行对应一条结果；多条例句请用竖线字符 `｜` 连接（例如：句子1｜句子2）。\n"
        + "2) 行的开头必须保留序号和一个分隔符 '|||' 用来将输入和输出分开，例如：1|||句子1｜句子2\n"
        + "3) 例句中必须出现给定的词，且不要改变词的字形。\n"
        + "4) 每个例句控制在 3-20 个汉字为宜，尽量自然、常用。\n"
        + "5) 如果无法生成合适例句，请仅返回序号和分隔符，分隔符后留空（例如：2|||\n）。\n\n"
        + "输入：\n"
        + "\n".join(lines)
        + "\n\n请严格按照格式输出，每行一条，形如：序号|||例句或空。\n"
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个中文例句生成器，擅长根据词、拼音、词性和释义生成简短自然的例句。"},
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

        # Parse lines: expect lines like '1|||例句1｜例句2' or '2|||' for empty
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
    """Process a CSV file, generate examples for empty rows.

    Returns (rows_seen, rows_updated, samples) where samples are up to 3 generated example strings for reporting.
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

        # Use fixed column names present in the project CSVs.
        # Fail fast if they are missing to avoid guessing.
        try:
            hanzi_idx = header.index(TAG)
            pinyin_idx = header.index('pinyin')
            pos_idx = header.index('pos')
            def_idx = header.index('definition')
        except ValueError as e:
            raise RuntimeError(f"Required column missing in {src}: {e}")

        # example column must exist; if not, append it
        if 'example' in header:
            ex_idx = header.index('example')
        else:
            header.append('example')
            ex_idx = len(header) - 1

        rows: list[list[str]] = [r for r in reader]
        # ensure every row has correct length
        for i, row in enumerate(rows):
            if len(row) < len(header):
                rows[i] = row + [''] * (len(header) - len(row))

        # rows_seen = number of data rows in this file
        rows_seen = len(rows)

        # Collect indices that need examples
        to_fill: List[int] = []
        for i, row in enumerate(rows):
            example_val = row[ex_idx].strip() if ex_idx < len(row) else ''
            if not example_val:
                to_fill.append(i)

        # In dry-run mode, only actually call the LLM for the first sample_batches_to_call batches
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
                    'word': row[hanzi_idx].strip() if hanzi_idx < len(row) else '',
                    'pinyin': row[pinyin_idx].strip() if pinyin_idx < len(row) else '',
                    'pos': row[pos_idx].strip() if pos_idx < len(row) else '',
                    'definition': row[def_idx].strip() if def_idx < len(row) else '',
                })

            # Decide whether to call LLM for this batch
            call_llm = True
            if dry_run and sample_batches_to_call is not None and b_idx >= sample_batches_to_call:
                call_llm = False

            generated_list: List[str]
            if call_llm:
                generated_list = generate_examples_batch(items)
            else:
                generated_list = [''] * len(items)

            # assign back
            for idx_in_batch, row_idx in enumerate(batch):
                gen = generated_list[idx_in_batch].strip() if idx_in_batch < len(generated_list) else ''
                if gen:
                    rows[row_idx][ex_idx] = gen
                    rows_updated += 1
                    if len(samples) < 3:
                        samples.append(f"{src.name}: {rows[row_idx][hanzi_idx]} -> {gen}")

            # rate limit
            time.sleep(sleep_s)

            # progress for this file: print batch progress inline
            try:
                pct = (b_idx + 1) / total_batches * 100 if total_batches > 0 else 100
                print(f"Processing {src.name}: batch {b_idx+1}/{total_batches} ({pct:.0f}%)\r", end='', flush=True)
            except Exception:
                pass

            # Save only the current batch's data to a batch-suffixed file: <original>.batch<N>.csv
            if not dry_run and dst is not None:
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    base = dst.stem
                    suff = f".batch{b_idx+1}.csv"
                    batch_file = dst.with_name(base + suff)
                    with batch_file.open('w', encoding='utf-8-sig', newline='') as out_f:
                        writer = csv.writer(out_f)
                        writer.writerow(header)
                        # Write only the rows in the current batch
                        writer.writerows([rows[row_idx] for row_idx in batch])
                except Exception as e:
                    print(f"Warning: failed to write batch results for {dst}: {e}")

    if not dry_run and dst is not None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open('w', encoding='utf-8-sig', newline='') as out_f:
            writer = csv.writer(out_f)
            writer.writerow(header)
            writer.writerows(rows)

    return rows_seen, rows_updated, samples


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate example sentences using LLM for CSV rows missing examples')
    parser.add_argument('--src', required=False, default='jjhy_csv/core_csv_no_exmaples/', help='Source directory with CSVs')
    parser.add_argument('--dst', required=False, default='jjhy_csv/core_csv_with_generated_examples/', help='Destination directory to write updated CSVs')
    parser.add_argument('--dry-run', action='store_true', help='Do not write files; only print counts and samples')
    parser.add_argument('--sleep', type=float, default=0.25, help='Seconds to sleep between LLM calls (rate limit)')
    parser.add_argument('--batch-size', type=int, default=100, help='Number of rows to send to LLM in one batch')
    args = parser.parse_args()

    src_dir = Path(args.src)
    dst_dir = Path(args.dst)

    if not src_dir.exists() or not src_dir.is_dir():
        print(f"Source directory does not exist: {src_dir}")
        return 2

    total_seen = 0
    total_updated = 0
    samples_all: list[str] = []

    files = list(find_csv_files(src_dir))
    total_files = len(files)
    for idx, src_file in enumerate(tqdm(files, desc='files')):
        dst_file = dst_dir / src_file.name if not args.dry_run else None
        seen, updated, samples = process_file(src_file, dst_file, dry_run=args.dry_run, sleep_s=args.sleep, batch_size=args.batch_size)
        total_seen += seen
        total_updated += updated
        samples_all.extend(samples)
        # clear inline batch progress and print file summary
        print('\n' + f"{src_file.name}: rows_seen={seen}, rows_updated={updated}")

    print(f"Summary: total rows seen={total_seen}, total rows updated={total_updated}")
    if samples_all:
        print("Sample generated examples:")
        for s in samples_all:
            print(" - ", s)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
