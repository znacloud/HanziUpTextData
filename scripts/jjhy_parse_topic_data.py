import argparse
import csv
import os
import glob
import re
from typing import Optional, Tuple


ROOT_RE = re.compile(
    r"<font[^>]*>\s*(?:<a[^>]*>)?\s*(?P<root>\d{1,3})\s+(?P<name>[^<]+?)(?:</a>)?\s*</font>",
    re.IGNORECASE,
)

PARENT_RE = re.compile(
    r"<font[^>]*>\s*(?:<a[^>]*>)?\s*(?P<root>\d{1,3})\.(?P<parent>\d{1,3})\s+(?P<name>[^<]+?)(?:</a>)?\s*</font>",
    re.IGNORECASE,
)

CATEGORY_RE = re.compile(
    r"<font[^>]*>\s*(?:<a[^>]*>)?\s*(?P<root>\d{1,3})\.(?P<parent>\d{1,3})\.(?P<cat>\d{1,3})\s+(?P<name>[^<]+?)(?:</a>)?\s*</font>",
    re.IGNORECASE,
)

ITEM_RE = re.compile(
    r"^\s*<A\b[^>]*>\s*(?P<item>[^<]+)\s*</a>\s*<sub>\s*(?P<rank>\d+)\s*</sub>",
    re.IGNORECASE,
)


def parse_root(line: str) -> Optional[Tuple[str, str]]:
    match = ROOT_RE.search(line)
    if match and not PARENT_RE.search(line) and not CATEGORY_RE.search(line):
        return match.group("name").strip(), match.group("root").strip()
    return None


def parse_parent(line: str) -> Optional[Tuple[str, str, str]]:
    # Ensure it's parent-level (two segments), not category (three segments)
    if CATEGORY_RE.search(line):
        return None
    match = PARENT_RE.search(line)
    if match:
        return (
            match.group("name").strip(),
            match.group("root").strip(),
            match.group("parent").strip(),
        )
    return None


def parse_category(line: str) -> Optional[Tuple[str, str, str, str]]:
    match = CATEGORY_RE.search(line)
    if match:
        return (
            match.group("name").strip(),
            match.group("root").strip(),
            match.group("parent").strip(),
            match.group("cat").strip(),
        )
    return None


def parse_item(line: str) -> Optional[Tuple[str, str]]:
    match = ITEM_RE.search(line)
    if match:
        return match.group("item").strip(), match.group("rank").strip()
    return None


def parse_file_to_rows(text: str, context: Optional[dict] = None):
    # Initialize from provided context to allow cross-file continuity
    current_root_name: Optional[str] = (context or {}).get("root_category") if context else None
    current_root_sn: Optional[str] = (context or {}).get("root_sn") if context else None
    current_parent_name: Optional[str] = (context or {}).get("parent_category") if context else None
    current_parent_sn: Optional[str] = (context or {}).get("parent_sn") if context else None
    current_category_name: Optional[str] = (context or {}).get("category") if context else None
    current_category_sn: Optional[str] = (context or {}).get("sn") if context else None

    rows = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Order matters: category -> parent -> root -> item
        cat = parse_category(line)
        if cat:
            name, r_sn, p_sn, c_sn = cat
            current_root_sn = r_sn
            current_parent_sn = p_sn
            current_category_sn = c_sn
            current_category_name = name
            # Category line also implies parent/root context already parsed earlier
            continue

        parent = parse_parent(line)
        if parent:
            name, r_sn, p_sn = parent
            current_root_sn = r_sn
            current_parent_sn = p_sn
            current_parent_name = name
            # Reset lower level when parent changes
            current_category_name = None
            current_category_sn = None
            continue

        root = parse_root(line)
        if root:
            name, r_sn = root
            current_root_name = name
            current_root_sn = r_sn
            # Reset lower levels when root changes
            current_parent_name = None
            current_parent_sn = None
            current_category_name = None
            current_category_sn = None
            continue

        item = parse_item(line)
        if item:
            item_text, item_rank = item
            rows.append({
                "root_category": current_root_name or "",
                "root_sn": current_root_sn or "",
                "parent_category": current_parent_name or "",
                "parent_sn": current_parent_sn or "",
                "category": current_category_name or "",
                "sn": current_category_sn or "",
                "item": item_text,
                "item_rank": item_rank,
            })

    # Write back context for cross-file continuity
    if context is not None:
        context.update({
            "root_category": current_root_name,
            "root_sn": current_root_sn,
            "parent_category": current_parent_name,
            "parent_sn": current_parent_sn,
            "category": current_category_name,
            "sn": current_category_sn,
        })

    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Parse HTML-like category index into CSV rows"
    )
    parser.add_argument(
        "input",
        help="Input file or directory. If a directory, parses all jjhy-hanzi-topics-*.html inside.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output CSV file path (default: <input_basename>_parsed.csv or <dir>_xdhy_parsed.csv)",
    )
    args = parser.parse_args()

    input_path = args.input

    rows = []
    files_to_parse = []
    if os.path.isdir(input_path):
        pattern = os.path.join(input_path, "jjhy-hanzi-topics-*.html")
        files_to_parse = sorted(glob.glob(pattern))
        if not files_to_parse:
            print(f"No files matched pattern: {pattern}")
    else:
        files_to_parse = [input_path]

    # Maintain parsing context across files
    context = {}
    for fp in files_to_parse:
        with open(fp, "r", encoding="utf-8") as f:
            text = f.read()
        rows.extend(parse_file_to_rows(text, context))

    if args.output:
        output_path = args.output
    else:
        if os.path.isdir(input_path):
            base = os.path.basename(os.path.normpath(input_path)) or "raw_data"
            output_path = os.path.join(input_path, f"{base}_xdhy_parsed.csv")
        else:
            output_path = os.path.splitext(input_path)[0] + "_parsed.csv"

    fieldnames = [
        "root_category",
        "root_sn",
        "parent_category",
        "parent_sn",
        "category",
        "sn",
        "item",
        "item_rank",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()


