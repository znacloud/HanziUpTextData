import csv
import sys
from pathlib import Path


def extract_unique_term_pinyin_pairs_from_csv(csv_path: Path) -> tuple[str | None, list[tuple[str, str]]]:
    """Read a CSV file and return the term column name (either 'hanzi' or 'cihui')
    and a list of unique (term, pinyin) pairs preserving order.
    """
    pairs: list[tuple[str, str]] = []
    seen_pairs: set[tuple[str, str]] = set()

    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            return None, pairs

        # Resolve pinyin field
        pinyin_field: str | None = None
        for field in reader.fieldnames:
            if field == "pinyin":
                pinyin_field = field
                break
        if pinyin_field is None:
            for field in reader.fieldnames:
                if field.lower() == "pinyin":
                    pinyin_field = field
                    break

        # Resolve term field: prefer exact match 'cihui' or 'hanzi'; then case-insensitive
        term_field: str | None = None
        for candidate in ("cihui", "hanzi"):
            if candidate in (reader.fieldnames or []):
                term_field = candidate
                break
        if term_field is None:
            lower_map = {f.lower(): f for f in (reader.fieldnames or [])}
            for candidate in ("cihui", "hanzi"):
                if candidate in lower_map:
                    term_field = lower_map[candidate]
                    break

        if pinyin_field is None or term_field is None:
            return term_field, pairs

        for row in reader:
            term_value = (row.get(term_field) or "").strip()
            pinyin_value = (row.get(pinyin_field) or "").strip()
            if not term_value or not pinyin_value:
                continue
            key = (term_value, pinyin_value)
            if key not in seen_pairs:
                seen_pairs.add(key)
                pairs.append(key)

    return term_field, pairs


def write_term_pinyin_pairs_to_csv(term_field: str, pairs: list[tuple[str, str]], output_csv_path: Path) -> None:
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with output_csv_path.open("w", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file)
        writer.writerow([term_field, "pinyin"])  # header
        for term_value, pinyin_value in pairs:
            writer.writerow([term_value, pinyin_value])


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    input_dir = project_root / "jjhy_csv" / "core_csv"
    output_dir = project_root / "jjhy_csv" / "core_pinyin"

    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input directory not found: {input_dir}")
        return 1

    csv_files = sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == ".csv"]) 
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return 0

    total_written = 0
    for csv_file in csv_files:
        try:
            term_field, pairs = extract_unique_term_pinyin_pairs_from_csv(csv_file)
        except Exception as exc:
            print(f"Failed to process {csv_file.name}: {exc}")
            continue

        if not term_field or not pairs:
            print(f"No term+pinyin pairs found in {csv_file.name}; skipping write")
            continue

        output_csv = output_dir / csv_file.name
        try:
            write_term_pinyin_pairs_to_csv(term_field, pairs, output_csv)
        except Exception as exc:
            print(f"Failed to write {output_csv}: {exc}")
            continue

        total_written += 1
        print(f"Wrote {len(pairs)} unique {term_field}+pinyin pairs to {output_csv.relative_to(project_root)}")

    print(f"Done. Wrote outputs for {total_written} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


