#!/usr/bin/env python3
"""Filter rows whose example column is empty in CSV files.

Usage:
  python scripts/filter_no_examples.py --src <src_dir> --dst <dst_dir> [--dry-run]

By default this scans all .csv files in src_dir and writes filtered files to dst_dir
preserving filenames. If --dry-run is set, it only prints counts and does not write files.
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from typing import Iterable


def find_csv_files(src_dir: Path) -> Iterable[Path]:
    for p in sorted(src_dir.iterdir()):
        if p.is_file() and p.suffix.lower() == ".csv":
            yield p


def detect_example_column(header: list[str]) -> int | None:
    # prefer exact match 'example', but also accept variants like 'examples', '示例' if present
    lower = [h.strip().lower() for h in header]
    for name in ("example", "examples", "示例"):
        if name in lower:
            return lower.index(name)
    # fallback: if header has at least 1 column named with ascii letters and we can't find, try 'example' literally
    return None


def process_file(src: Path, dst: Path | None, dry_run: bool = False) -> tuple[int,int]:
    """Return (kept_rows, removed_rows) not counting header."""
    kept = 0
    removed = 0
    with src.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return (0, 0)

        ex_idx = detect_example_column(header)
        if ex_idx is None:
            # try to find a header that contains 'example' substring
            for i, h in enumerate(header):
                if "example" in h.strip().lower() or "示例" in h:
                    ex_idx = i
                    break

        rows_to_write: list[list[str]] = []
        for row in reader:
            # if row shorter than header, extend
            if len(row) <= (ex_idx or 0):
                example_val = ""
            else:
                example_val = row[ex_idx].strip() if ex_idx is not None and ex_idx < len(row) else ""
            if not example_val:
                kept += 1
                rows_to_write.append(row)
            else:
                removed += 1

    if not dry_run and dst is not None and len(rows_to_write) > 0:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("w", encoding="utf-8-sig", newline="") as out_f:
            writer = csv.writer(out_f)
            writer.writerow(header)
            writer.writerows(rows_to_write)

    return kept, removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter CSV rows with empty example column")
    parser.add_argument("--src", required=False, default="jjhy_csv/core_csv_reranked_with_updated_pinyin/", help="Source directory")
    parser.add_argument("--dst", required=False, default="jjhy_csv/core_csv_no_exmaples/", help="Destination directory")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files; only print counts")
    args = parser.parse_args()

    src_dir = Path(args.src)
    dst_dir = Path(args.dst)

    if not src_dir.exists() or not src_dir.is_dir():
        print(f"Source directory does not exist: {src_dir}")
        return 2

    total_kept = 0
    total_removed = 0

    for src_file in find_csv_files(src_dir):
        dst_file = dst_dir / src_file.name if not args.dry_run else None
        kept, removed = process_file(src_file, dst_file, dry_run=args.dry_run)
        total_kept += kept
        total_removed += removed
        print(f"{src_file.name}: kept={kept}, removed={removed}")

    print(f"Summary: total kept={total_kept}, total removed={total_removed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
