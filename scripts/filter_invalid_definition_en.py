#!/usr/bin/env python3
"""
Filter CSV files whose `definition_en` column contains Chinese characters.

Usage: python scripts/filter_invalid_definition_en.py

This script reads all CSV files from
`jjhy_csv/core_csv_with_generated_definitions` and writes rows where
`definition_en` contains any CJK Unified Ideographs (\u4e00-\u9fff) to the
matching filename under
`jjhy_csv/core_csv_with_invalid_definition_en`.

The script prefers pandas if available for robust CSV handling, and falls
back to the standard csv module otherwise.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    import pandas as pd
except Exception:
    pd = None


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "jjhy_csv" / "core_csv_with_generated_definitions"
OUT_DIR = ROOT / "jjhy_csv" / "core_csv_with_invalid_definition_en"

CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")


def has_chinese(s: str) -> bool:
    if not isinstance(s, str):
        return False
    return bool(CHINESE_RE.search(s))


def process_with_pandas(src_path: Path, out_path: Path) -> int:
    df = pd.read_csv(src_path)
    if 'definition_en' not in df.columns:
        print(f"Skipping {src_path.name}: no 'definition_en' column")
        return 0
    mask = df['definition_en'].astype(str).apply(has_chinese)
    filtered = df[mask]
    if not filtered.empty:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        filtered.to_csv(out_path, index=False)
    return int(mask.sum())


def process_with_csv_module(src_path: Path, out_path: Path) -> int:
    import csv

    with src_path.open('r', encoding='utf-8', newline='') as rf:
        reader = csv.DictReader(rf)
        if 'definition_en' not in reader.fieldnames:
            print(f"Skipping {src_path.name}: no 'definition_en' column")
            return 0
        rows = [r for r in reader if has_chinese(r.get('definition_en'))]

    if rows:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open('w', encoding='utf-8', newline='') as wf:
            writer = csv.DictWriter(wf, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    return len(rows)


def main() -> int:
    if not SRC_DIR.exists():
        print(f"Source directory not found: {SRC_DIR}")
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    total_files = 0
    total_rows = 0

    for p in sorted(SRC_DIR.glob('*.csv')):
        total_files += 1
        out_path = OUT_DIR / p.name
        try:
            if pd is not None:
                count = process_with_pandas(p, out_path)
            else:
                count = process_with_csv_module(p, out_path)
            print(f"{p.name}: {count} rows with Chinese characters in definition_en")
            total_rows += count
        except Exception as e:
            print(f"Error processing {p.name}: {e}")

    print(f"Processed {total_files} files. Found {total_rows} filtered rows total.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
