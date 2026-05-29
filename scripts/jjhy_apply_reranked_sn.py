import re
from pathlib import Path
from typing import Tuple

import pandas as pd

TAG = "hanzi"

def extract_bucket_number(filename: str) -> str:
	"""Extract the numeric bucket from filenames like 'jjhy_cihui_parsed_10000_filtered.csv'."""
	match = re.search(f"jjhy_{TAG}_parsed_(\d+)_filtered\.csv$", filename)
	if not match:
		raise ValueError(f"Unexpected core csv filename format: {filename}")
	return match.group(1)


def build_paths(base_dir: Path, bucket: str) -> Tuple[Path, Path]:
	core_csv_dir = base_dir / "jjhy_csv" / "core_csv"
	reranked_dir = base_dir / "jjhy_csv" / "reranked_definitions"
	core_filename = f"jjhy_{TAG}_parsed_{bucket}_filtered.csv"
	reranked_filename = f"reranked_{TAG}_{bucket}_final.csv"
	return core_csv_dir / core_filename, reranked_dir / reranked_filename


def apply_reranked_sn_to_core(core_csv_path: Path, reranked_csv_path: Path) -> pd.DataFrame:
	"""Merge core CSV with reranked CSV on (rank, sn) and replace sn with new_sn when available."""
	# Read data
	core_df = pd.read_csv(core_csv_path)
	reranked_df = pd.read_csv(reranked_csv_path)

	# Validate required columns
	for col in ["rank", "sn"]:
		if col not in core_df.columns:
			raise KeyError(f"Column '{col}' missing in core csv: {core_csv_path}")
	for col in ["rank", "sn", "new_sn"]:
		if col not in reranked_df.columns:
			raise KeyError(f"Column '{col}' missing in reranked csv: {reranked_csv_path}")

	# Coerce dtypes for reliable merge
	core_df["rank"] = pd.to_numeric(core_df["rank"], errors="coerce").astype("Int64")
	core_df["sn"] = pd.to_numeric(core_df["sn"], errors="coerce").astype("Int64")
	reranked_map = reranked_df[["rank", "sn", "new_sn"]].copy()
	reranked_map["rank"] = pd.to_numeric(reranked_map["rank"], errors="coerce").astype("Int64")
	reranked_map["sn"] = pd.to_numeric(reranked_map["sn"], errors="coerce").astype("Int64")
	reranked_map["new_sn"] = pd.to_numeric(reranked_map["new_sn"], errors="coerce").astype("Int64")

	# Merge to fetch new_sn
	merged = core_df.merge(reranked_map, on=["rank", "sn"], how="left")
	updated_count = int(merged["new_sn"].notna().sum())

	# Replace sn where new_sn exists
	merged["sn"] = merged["new_sn"].combine_first(merged["sn"])  # prefer new_sn
	merged.drop(columns=["new_sn"], inplace=True)

	# Cast back to int where possible
	try:
		merged["sn"] = merged["sn"].astype(int)
		merged["rank"] = merged["rank"].astype(int)
	except Exception:
		# Keep nullable ints if any NaNs slipped through
		merged["sn"] = merged["sn"].astype("Int64")
		merged["rank"] = merged["rank"].astype("Int64")

	print(f"Updated {updated_count} rows in {core_csv_path.name}")
	# sort by rank and sn
	merged = merged.sort_values(by=["rank", "sn"])
	return merged


def main() -> None:
	base_dir = Path(__file__).resolve().parent.parent
	core_csv_dir = base_dir / "jjhy_csv" / "core_csv"
	out_dir = base_dir / "jjhy_csv" / "core_csv_reranked"
	out_dir.mkdir(parents=True, exist_ok=True)

	core_files = sorted(core_csv_dir.glob(f"jjhy_{TAG}_parsed_*_filtered.csv"))
	if not core_files:
		print(f"No core CSV files found in {core_csv_dir}")
		return

	for core_csv_path in core_files:
		try:
			bucket = extract_bucket_number(core_csv_path.name)
		except ValueError as e:
			print(f"Skipping file due to name mismatch: {core_csv_path.name} ({e})")
			continue

		_, reranked_csv_path = build_paths(base_dir, bucket)
		if not reranked_csv_path.exists():
			print(f"Reranked file missing, skipping: {reranked_csv_path.name}")
			continue

		try:
			updated_df = apply_reranked_sn_to_core(core_csv_path, reranked_csv_path)
			# Preserve original column order from core CSV
			original_cols = list(pd.read_csv(core_csv_path, nrows=0).columns)
			updated_df = updated_df[original_cols]
			out_path = out_dir / core_csv_path.name
			updated_df.to_csv(out_path, index=False)
			print(f"Saved: {out_path}")
		except Exception as e:
			print(f"Error processing {core_csv_path.name}: {e}")


if __name__ == "__main__":
	main()


