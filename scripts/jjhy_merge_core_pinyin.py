import csv
from pathlib import Path


def read_term_pinyin_pairs_from_csv(csv_path: Path) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return pairs

        # Detect columns
        fieldnames = reader.fieldnames
        pinyin_field = next((c for c in fieldnames if c == "pinyin"), None)
        if pinyin_field is None:
            pinyin_field = next((c for c in fieldnames if c.lower() == "pinyin"), None)

        term_field = None
        # Prefer cihui over hanzi when both exist
        if "cihui" in fieldnames:
            term_field = "cihui"
        elif "hanzi" in fieldnames:
            term_field = "hanzi"
        else:
            lower_map = {c.lower(): c for c in fieldnames}
            for candidate in ("cihui", "hanzi"):
                if candidate in lower_map:
                    term_field = lower_map[candidate]
                    break

        if not pinyin_field or not term_field:
            return pairs

        for row in reader:
            term = (row.get(term_field) or "").strip()
            pinyin = (row.get(pinyin_field) or "").strip()
            if not term or not pinyin:
                continue
            pairs.append((term, pinyin))
    return pairs


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    pinyin_dir = project_root / "jjhy_csv" / "core_pinyin"
    output_csv = project_root / "jjhy_csv" / "jjhy_pinyin_all.csv"

    csv_files = sorted([p for p in pinyin_dir.iterdir() if p.is_file() and p.suffix.lower() == ".csv"]) 
    if not csv_files:
        print(f"No CSV files found in {pinyin_dir}")
        return 1

    deduped: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for csv_file in csv_files:
        for pair in read_term_pinyin_pairs_from_csv(csv_file):
            if pair not in seen:
                seen.add(pair)
                deduped.append(pair)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["term", "pinyin"])  # normalized header
        for term, pinyin in deduped:
            writer.writerow([term, pinyin])

    print(f"Wrote {len(deduped)} unique term+pinyin pairs to {output_csv.relative_to(project_root)} from {len(csv_files)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


