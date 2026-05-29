import pandas as pd

# File paths
file_extended = 'others/hanzi_examples_extended_from_filtered.csv'
file_v6 = 'others/hanzi_examples_v6_generated.csv'
file_validation = 'others/hanzi_examples_validation.csv'
output_file = 'others/hanzi_examples_extended_vs_generated.csv'

# Columns to use
cols_extended = ['definition_id', 'extend_example_cn']
cols_v6 = ['definition_id', 'example_cn']
cols_validation = ['definition_id', 'hanzi', 'pinyin', 'definition_cn', 'pos']

# Read only necessary columns from each file
df_extended = pd.read_csv(file_extended, usecols=cols_extended, dtype=str)
df_v6 = pd.read_csv(file_v6, usecols=cols_v6, dtype=str)
df_validation = pd.read_csv(file_validation, usecols=cols_validation, dtype=str)

# Merge step 1: left join v6 example_cn onto extended
merged = pd.merge(df_extended, df_v6, on='definition_id', how='left')
# Merge step 2: left join validation info onto result
merged = pd.merge(merged, df_validation, on='definition_id', how='left')

# sort columns
merged = merged[['definition_id','hanzi', 'pinyin', 'pos', 'definition_cn', 'extend_example_cn', 'example_cn', ]]

# drop rows where hanzi column is empty
merged = merged[merged['hanzi'].notna()]

# Save to output
merged.to_csv(output_file, index=False)

print(f'Merged file saved to {output_file}') 