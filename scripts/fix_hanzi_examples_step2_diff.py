import pandas as pd

# File paths
qw_path = 'others/hanzi_examples_better_selection_QW.csv'
ds_path = 'others/hanzi_examples_better_selection_DS.csv'
out_path = 'others/hanzi_examples_better_selection_diff.csv'

# Columns to join on (all except 'better')
key_cols = [
    'definition_id', 'hanzi', 'pinyin', 'pos', 'definition_cn', 'example_1', 'example_2'
]

# Read both files
qw = pd.read_csv(qw_path, dtype=str)
ds = pd.read_csv(ds_path, dtype=str)

# Rename 'better' columns for clarity
qw = qw.rename(columns={'better': 'QW'})
ds = ds.rename(columns={'better': 'DS'})

# Merge on all columns except 'better'
merged = pd.merge(qw, ds, on=key_cols, how='inner')

# Extract rows where 'QW' and 'DS' differ
mask = merged['QW'] != merged['DS']
diff = merged.loc[mask, key_cols + ['DS', 'QW']]

# Save to CSV
if not diff.empty:
    diff.to_csv(out_path, index=False)
    print(f"Saved {len(diff)} differing rows to {out_path}")
else:
    print("No differences found in the 'better' column.") 