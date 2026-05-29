#!/usr/bin/env python3
"""
override_definitions.py

Walks source CSV files in
  jjhy_csv/core_csv_with_invalid_definition_en
and uses rows to override matching rows in
  jjhy_csv/core_csv_with_generated_definitions

Matching key: (rank, sn)

Default behavior: source row overrides target row only if source.rank < target.rank
(i.e., lower rank value wins). Use --prefer-higher to flip.

Options:
  --dry-run    : don't write files, just report changes
  --backup     : create a .bak copy of each target file before modifying
  --force      : always override regardless of rank
  --prefer-higher : prefer rows with higher rank value when deciding overrides

Assumptions:
 - CSVs have headers and include columns 'rank' and 'sn'.
 - Rows correspond when both 'rank' and 'sn' match exactly (string match).

"""
import argparse
import csv
import os
import shutil
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / 'core_csv_with_invalid_definition_en'
TGT_DIR = Path(__file__).resolve().parents[1] / 'core_csv_with_generated_definitions'


def find_target_file(src_path: Path) -> Path:
    # Normalize name: remove trailing (m) before extension and map to .csv
    name = src_path.name
    name = name.replace('(m)', '')
    # also allow _filtered(m).csv -> _filtered.csv
    candidate = TGT_DIR / name
    if candidate.exists():
        return candidate
    # fallback: try stripping suffixes like '(m)'
    alt = name.replace('(m)', '')
    candidate = TGT_DIR / alt
    if candidate.exists():
        return candidate
    # try matching by numeric part: find file in tgt with same prefix before last underscore
    for p in TGT_DIR.glob('*.csv'):
        if p.stem.replace('(m)', '') == Path(name).stem.replace('(m)', ''):
            return p
    return None


def read_csv_rows(path: Path):
    # Read as text and strip optional Markdown code fences like ```csv ... ```
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    # remove leading ``` or ```csv lines
    if lines and lines[0].strip().startswith('```'):
        # drop the first line
        lines = lines[1:]
        # if there's a trailing fence, drop it
        if lines and lines[-1].strip().startswith('```'):
            lines = lines[:-1]
    cleaned = '\n'.join(lines)
    # Use csv.DictReader on cleaned content
    from io import StringIO
    reader = csv.DictReader(StringIO(cleaned))
    raw_fieldnames = reader.fieldnames or []
    # normalize fieldnames (strip BOM and whitespace)
    def norm(k):
        if k is None:
            return ''
        return k.replace('\ufeff', '').strip()
    fieldnames = [norm(fn) for fn in raw_fieldnames]

    rows = []
    for raw in reader:
        new = {}
        for k, v in raw.items():
            nk = norm(k)
            new[nk] = v
        rows.append(new)
    return fieldnames, rows


def write_csv_rows(path: Path, fieldnames, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--backup', action='store_true')
    p.add_argument('--force', action='store_true')
    p.add_argument('--debug', action='store_true', help='print debug info about key sets and intersections')
    p.add_argument('--prefer-higher', action='store_true', help='prefer higher rank value when deciding override')
    p.add_argument('--src-dir', default=str(SRC_DIR))
    p.add_argument('--tgt-dir', default=str(TGT_DIR))
    args = p.parse_args()

    src_dir = Path(args.src_dir)
    tgt_dir = Path(args.tgt_dir)

    if not src_dir.exists():
        print(f"Source dir not found: {src_dir}")
        return
    if not tgt_dir.exists():
        print(f"Target dir not found: {tgt_dir}")
        return

    src_files = sorted(src_dir.glob('*.csv'))
    total_changed = 0
    total_checked = 0

    for srcf in src_files:
        tgtf = find_target_file(srcf)
        if tgtf is None:
            print(f"No matching target for {srcf.name}, skipping")
            continue

        print(f"Processing \n  src: {srcf}\n  tgt: {tgtf}")
        src_fields, src_rows = read_csv_rows(srcf)
        tgt_fields, tgt_rows = read_csv_rows(tgtf)

        # unify fieldnames (preserve target order)
        fieldnames = tgt_fields
        # build index on target by (rank,sn)
        tgt_index = {}
        for i, r in enumerate(tgt_rows):
            key = (r.get('rank','').strip(), r.get('sn','').strip())
            tgt_index[key] = i

        if args.debug:
            src_keys = [ (s.get('rank','').strip(), s.get('sn','').strip()) for s in src_rows ]
            tgt_keys = list(tgt_index.keys())
            set_src = set(src_keys)
            set_tgt = set(tgt_keys)
            inter = set_src & set_tgt
            print(f"    debug: src_rows={len(src_rows)} tgt_rows={len(tgt_rows)} src_keys={len(set_src)} tgt_keys={len(set_tgt)} intersection={len(inter)}")
            if len(inter) > 0:
                print("    sample intersection:")
                for k in list(inter)[:10]:
                    print(f"      {k}")
            else:
                print("    sample src keys:")
                for k in list(set_src)[:10]:
                    print(f"      {k}")
                print("    sample tgt keys:")
                for k in list(set_tgt)[:10]:
                    print(f"      {k}")

        changes = []

        for s in src_rows:
            total_checked += 1
            key = (s.get('rank','').strip(), s.get('sn','').strip())
            if key in tgt_index:
                ti = tgt_index[key]
                trow = tgt_rows[ti]
                # compare rank numeric if possible
                try:
                    s_rank = float(s.get('rank','').strip())
                except Exception:
                    s_rank = None
                try:
                    t_rank = float(trow.get('rank','').strip())
                except Exception:
                    t_rank = None

                # Override when rank+sn match (user requested).
                # --force still allows unconditional override but behavior is the same here.
                do_override = True

                if do_override:
                    # copy values from source into target for common fields
                    for k, v in s.items():
                        if k in trow:
                            trow[k] = v
                    changes.append((key, trow, s))

        if changes:
            print(f"  Will update {len(changes)} rows in {tgtf.name}")
            total_changed += len(changes)
            if args.dry_run:
                for k, new, src in changes[:10]:
                    print(f"    change {k} -> definition_en (src): {src.get('definition_en','')[:60]!r}")
                if len(changes) > 10:
                    print(f"    ... and {len(changes)-10} more")
            else:
                if args.backup:
                    bak = tgtf.with_suffix(tgtf.suffix + '.bak')
                    shutil.copy2(tgtf, bak)
                    print(f"  backup saved to {bak}")
                # write updated rows keeping target field order
                write_csv_rows(tgtf, fieldnames, tgt_rows)
                print(f"  wrote {tgtf}")
        else:
            print(f"  No changes needed for {tgtf.name}")

    print(f"Done. checked {total_checked} source rows, total changes: {total_changed}")


if __name__ == '__main__':
    main()
