import pandas as pd

# File paths
diff_path = 'others/hanzi_examples_better_selection_diff.csv'
invalid_path = 'others/hanzi_examples_validation_QW_invalid.csv'
out_path = 'others/hanzi_examples_better_selection_diff_invalid.csv'

# Read the files
diff_df = pd.read_csv(diff_path, dtype=str)
invalid_df = pd.read_csv(invalid_path, dtype=str)

# Get the list of invalid definition_ids
invalid_definition_ids = invalid_df['definition_id'].tolist()

# Filter out rows where definition_id is not in the invalid list
filtered_df = diff_df[diff_df['definition_id'].isin(invalid_definition_ids)]

# Save the filtered result
filtered_df.to_csv(out_path, index=False)

print(f"Original diff file had {len(diff_df)} rows")
print(f"Invalid file had {len(invalid_definition_ids)} definition_ids")
print(f"Filtered file has {len(filtered_df)} rows")
print(f"Removed {len(diff_df) - len(filtered_df)} rows")
print(f"Filtered result saved to {out_path}") 