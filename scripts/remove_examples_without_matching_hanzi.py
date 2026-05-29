#!/usr/bin/env python3
"""Remove examples that don't contain the row's hanzi/cihui value.

Usage examples:
  # dry-run on a single file (default)
  python scripts/remove_examples_without_matching_hanzi.py --file jjhy_csv/core_csv_reranked_with_updated_pinyin/jjhy_cihui_parsed_5000_filtered.csv

  # write outputs to new files with _filtered.csv suffix
  python scripts/remove_examples_without_matching_hanzi.py --dir jjhy_csv/core_csv_reranked_with_updated_pinyin

  # overwrite originals (use carefully)
  python scripts/remove_examples_without_matching_hanzi.py --dir jjhy_csv/core_csv_reranked_with_updated_pinyin --inplace

This script is conservative by default (dry-run). Use --inplace to overwrite or --apply to write _filtered.csv files.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
from collections import Counter
from typing import List, Optional, Tuple


DEFAULT_DIR = os.path.join("jjhy_csv", "core_csv_reranked_with_updated_pinyin")


def detect_columns(header: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """Return (hanzi_col, example_col) chosen from header or (None,None)."""
    lower = [h.lower() for h in header]
    hanzi_candidates = ["hanzi", "cihui"]
    example_candidates = ["example", "examples"]

    hanzi_col = None
    example_col = None
    for c in hanzi_candidates:
        if c in lower:
            hanzi_col = header[lower.index(c)]
            break
    for c in example_candidates:
        if c in lower:
            example_col = header[lower.index(c)]
            break

    # fallbacks
    if not hanzi_col:
        # try any header that looks like a short chinese word (no spaces) and length<=6
        for h in header:
            if " " not in h and len(h) <= 10 and re.search(r"[\u4e00-\u9fff]", h):
                hanzi_col = h
                break
    if not example_col:
        for h in header:
            if "example" in h.lower() or "示例" in h:
                example_col = h
                break

    return hanzi_col, example_col


SEP_RE = re.compile(r"[|｜]+")


def split_examples(text: str) -> List[str]:
    if text is None:
        return []
    # Normalize fullwidth vertical bar to ascii for splitting
    s = text.strip()
    if s == "":
        return []
    parts = [p.strip() for p in SEP_RE.split(s) if p.strip()]
    # If splitting produced nothing, return the original as single example
    return parts or [s]


def choose_joiner(original: str) -> str:
    # try to detect the most common separator char in original string
    if not original:
        return "｜"
    candidates = ["｜", "|"]
    counts = {c: original.count(c) for c in candidates}
    best = max(counts.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else "｜"


def filter_examples_for_row(hanzi_value: str, example_text: str) -> Tuple[str, int, int]:
    """Return (new_example_text, kept_count, original_count)."""
    if not example_text:
        return "", 0, 0
    examples = split_examples(example_text)
    original_count = len(examples)
    hv = (hanzi_value or "").strip()
    if hv == "":
        # nothing to match against -> remove nothing
        return example_text, original_count, original_count

    kept = [ex for ex in examples if hv in ex]
    kept_count = len(kept)
    joiner = choose_joiner(example_text)
    new_text = joiner.join(kept) if kept else ""
    return new_text, kept_count, original_count


def process_file(path: str, write: bool = False, inplace: bool = False) -> Tuple[int, int, int]:
    """Process a single CSV file. Returns (rows_processed, examples_removed, rows_with_no_examples).

    If write is False, the function only gathers statistics.
    If write is True and inplace is False, writes a new file with suffix _filtered.csv.
    If write is True and inplace is True, overwrites the original file.
    """
    rows = 0
    examples_removed = 0
    rows_no_examples = 0

    out_rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        hanzi_col, example_col = detect_columns(header)
        if not hanzi_col or not example_col:
            print(f"Skipping {path}: could not detect hanzi/cihui column or example column (found hanzi={hanzi_col} example={example_col})")
            return 0, 0, 0
        for r in reader:
            rows += 1
            hv = r.get(hanzi_col, "")
            ex = r.get(example_col, "")
            new_ex, kept_count, orig_count = filter_examples_for_row(hv, ex)
            if kept_count < orig_count:
                examples_removed += (orig_count - kept_count)
            if new_ex == "":
                rows_no_examples += 1
            # set updated example field
            r[example_col] = new_ex
            out_rows.append(r)

    if write and rows > 0:
        out_path = path
        if not inplace:
            base, ext = os.path.splitext(path)
            out_path = f"{base}_filtered{ext}"
        # write with same fieldnames order
        with open(out_path, "w", newline="", encoding="utf-8-sig") as of:
            writer = csv.DictWriter(of, fieldnames=header)
            writer.writeheader()
            for r in out_rows:
                writer.writerow(r)

    return rows, examples_removed, rows_no_examples


def walk_and_process(directory: str, pattern: str = "*.csv", write: bool = False, inplace: bool = False, files: Optional[List[str]] = None) -> None:
    import glob

    if files:
        paths = files
    else:
        paths = sorted(glob.glob(os.path.join(directory, pattern)))

    total_rows = total_removed = total_no_examples = 0
    for p in paths:
        rows, removed, no_examples = process_file(p, write=write, inplace=inplace)
        print(f"Processed {os.path.basename(p)}: rows={rows}, removed_examples={removed}, rows_no_examples={no_examples}")
        total_rows += rows
        total_removed += removed
        total_no_examples += no_examples

    print("--- summary ---")
    print(f"files_processed={len(paths)} total_rows={total_rows} total_examples_removed={total_removed} rows_with_no_examples={total_no_examples}")


def main() -> None:
    p = argparse.ArgumentParser(description="Filter examples that don't include the hanzi/cihui value.")
    p.add_argument("--dir", default=DEFAULT_DIR, help="Directory containing CSVs (default: %(default)s)")
    p.add_argument("--file", help="Process only this single file (path relative to repo root or absolute)")
    p.add_argument("--inplace", action="store_true", help="Overwrite original files (dangerous). If not set, write _filtered.csv files when --apply used.")
    p.add_argument("--apply", action="store_true", help="Actually write output files. Default is dry-run (no files changed). Use with --inplace to overwrite originals.")
    p.add_argument("--pattern", default="*.csv", help="Glob pattern for CSV files in --dir")
    p.add_argument("--sample", type=int, default=5, help="Show sample rows changed (only in dry-run, max samples).")
    args = p.parse_args()

    target_files = None
    if args.file:
        target_files = [args.file]
    else:
        # expand dir
        target_files = None

    if args.apply:
        write = True
    else:
        write = False

    # If dry-run, we still want to run and print summaries
    if target_files:
        walk_and_process(".", pattern=args.pattern, write=write, inplace=args.inplace, files=target_files)
    else:
        walk_and_process(args.dir, pattern=args.pattern, write=write, inplace=args.inplace)


if __name__ == "__main__":
    main()
