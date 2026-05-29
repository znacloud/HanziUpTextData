import pandas as pd
import argparse
import os

def filter_hanzi_definitions(input_file, special_output_file, filtered_output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Find entries containing 'see' or 'same as' in definition_cn, but exclude those where 'same as' is in parentheses
    special_definitions = df[
        (df['definition_cn'].str.contains('～', na=False)) |
        (df['definition_cn'].str.contains('see', na=False)) |
        (df['definition_cn'].str.contains('same as', na=False))
    ]
    # Get the filtered entries (those without 'see' or 'same as' outside parentheses)
    filtered_definitions = df[
        ~(df['definition_cn'].str.contains('～', na=False)) &
        ~(df['definition_cn'].str.contains('see', na=False)) &
        ~(df['definition_cn'].str.contains('same as', na=False))
    ]

    # Print the results
    print(f"Found {len(special_definitions)} entries containing 'see' or 'same':\n")
    for _, row in special_definitions.iterrows():
        print(f"Definition ID: {row['definition_id']}")
        print(f"Definition CN: {row['definition_cn']}")
        print(f"Definition EN: {row['definition_en']}")
        print("-" * 80)

    # Create output directories if they don't exist
    os.makedirs(os.path.dirname(special_output_file), exist_ok=True)
    os.makedirs(os.path.dirname(filtered_output_file), exist_ok=True)

    # Save special entries to a CSV file
    special_definitions.to_csv(special_output_file, index=False)
    print(f"\nSpecial entries have been saved to '{special_output_file}'")

    # Save filtered entries to a CSV file
    filtered_definitions.to_csv(filtered_output_file, index=False)
    print(f"Filtered entries have been saved to '{filtered_output_file}'")
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total entries: {len(df)}")
    print(f"Special entries: {len(special_definitions)}")
    print(f"Filtered entries: {len(filtered_definitions)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter hanzi definitions and separate special entries.')
    parser.add_argument('--input', help='Path to the input CSV file')
    parser.add_argument('--special-output', help='Path to save special definitions')
    parser.add_argument('--filtered-output', help='Path to save filtered definitions')
    parser.add_argument('--default', action='store_true',
                       help='Use default paths (database_csv/hanzi_definition.csv, other/special_definitions.csv, database_csv/hanzi_definition_filtered.csv)')
    
    args = parser.parse_args()
    
    if args.default or not all([args.input, args.special_output, args.filtered_output]):
        input_file = 'raw_data/xdhy_rest_hanzi_definition.csv'
        special_output_file = 'others/xdhy_rest_hanzi_definition_special.csv'
        filtered_output_file = 'others/xdhy_rest_hanzi_definition_v1_filtered.csv'
    else:
        input_file = args.input
        special_output_file = args.special_output
        filtered_output_file = args.filtered_output
    
    filter_hanzi_definitions(input_file, special_output_file, filtered_output_file) 