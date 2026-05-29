import argparse
import os
import sys
import time
from pathlib import Path
import csv
from collections import defaultdict

try:
    import pandas as pd
except Exception:
    print("This script requires pandas. Install with: pip install pandas")
    sys.exit(2)


ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / 'jjhy_csv' / 'core_csv_with_generated_examples'
DST_DIR = ROOT / 'jjhy_csv' / 'core_csv_reranked_with_updated_pinyin'


def load_csv(path):
    # Read with pandas, keep dtype as string to avoid numeric coercion
    return pd.read_csv(path, dtype=str).fillna("")


def backup_file(path: Path):
    ts = time.strftime("%Y%m%dT%H%M%S")
    bak = path.with_suffix(path.suffix + f'.bak.{ts}')
    path.replace(path)  # no-op to ensure exists
    path.copy = None
    # Simple copy
    with path.open('rb') as r, bak.open('wb') as w:
        w.write(r.read())
    return bak


def write_csv(df, path: Path):
    # write without index
    df.to_csv(path, index=False)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true', help='Actually write changes (default: dry-run)')
    p.add_argument('--verbose', action='store_true')
    p.add_argument('--pattern', default='*.csv', help='Glob pattern to filter files')
    args = p.parse_args(argv)

    if not SRC_DIR.exists() or not DST_DIR.exists():
        print(f"Source or destination directory missing: {SRC_DIR} {DST_DIR}")
        sys.exit(1)

    src_files = {p.name: p for p in SRC_DIR.glob(args.pattern)}
    dst_files = {p.name: p for p in DST_DIR.glob(args.pattern)}

    common = sorted(set(src_files) & set(dst_files))
    if not common:
        print("No matching files found between source and destination.")
        return

    total_files = len(common)
    summary = []

    for idx, name in enumerate(common, 1):
        src_path = src_files[name]
        dst_path = dst_files[name]
        if args.verbose:
            print(f"[{idx}/{total_files}] Processing {name}")

        src_df = load_csv(src_path)
        dst_df = load_csv(dst_path)

        # Ensure rank and sn present
        for df, pth in ((src_df, src_path), (dst_df, dst_path)):
            if 'rank' not in df.columns or 'sn' not in df.columns:
                print(f"File {pth} missing required columns 'rank' and 'sn'. Skipping.")
                continue

        # Use tuple key
        src_df['_key'] = src_df['rank'].astype(str) + '::' + src_df['sn'].astype(str)
        dst_df['_key'] = dst_df['rank'].astype(str) + '::' + dst_df['sn'].astype(str)

        src_map = {k: row for k, row in src_df.set_index('_key').iterrows()}

        replace_count = 0
        replaced_keys = []

        # Columns to replace: all columns from src (except _key) will overwrite dst
        for i, row in dst_df.iterrows():
            k = row['_key']
            if k in src_map:
                replace_count += 1
                replaced_keys.append(k)
                # overwrite values in dst_df at i for columns present in src
                for col in src_df.columns:
                    if col == '_key':
                        continue
                    if col in dst_df.columns:
                        dst_df.at[i, col] = src_map[k][col]
                    else:
                        # if src has extra columns, add them to dst
                        dst_df.loc[i, col] = src_map[k][col]

        summary.append((name, replace_count, len(src_df), len(dst_df)))

        if args.verbose:
            print(f"  matched rows in src: {len(src_df)}, dst: {len(dst_df)}, replacements: {replace_count}")

        if args.apply and replace_count > 0:
            # # backup dst
            # ts = time.strftime("%Y%m%dT%H%M%S")
            # bak = dst_path.with_suffix(dst_path.suffix + f'.bak.{ts}')
            # # copy
            # with dst_path.open('rb') as r, bak.open('wb') as w:
            #     w.write(r.read())
            # write updated
            write_csv(dst_df.drop(columns=['_key']), dst_path)
            if args.verbose:
                print(f"  wrote updated file and backup {bak.name}")

    # print summary
    print("\nSummary:")
    total_repl = 0
    for name, repl, src_rows, dst_rows in summary:
        print(f"{name}: replacements={repl}, src_rows={src_rows}, dst_rows={dst_rows}")
        total_repl += repl
    print(f"Total files processed: {len(summary)}, total replacements: {total_repl}")


if __name__ == '__main__':
    main()
