import pandas as pd
import argparse
import os

def rerank_examples_by_frequency():
    """
    Rerank hanzi examples based on the frequency rank of the hanzi characters.
    Lower frequency_rank means higher frequency (more common).
    """
    
    print("Loading CSV files...")
    
    # Load the CSV files
    examples_df = pd.read_csv('database_csv/hanzi_examples_v7.csv')
    definitions_df = pd.read_csv('database_csv/hanzi_definition_v7_with_pos_updated.csv')
    pinyin_df = pd.read_csv('database_csv/hanzi_pinyin_v7_with_sn_updated.csv')
    
    print(f"Loaded {len(examples_df)} examples")
    print(f"Loaded {len(definitions_df)} definitions")
    print(f"Loaded {len(pinyin_df)} pinyin entries")
    
    # Merge examples with definitions to get pinyin_id
    print("Merging examples with definitions...")
    merged_df = examples_df.merge(
        definitions_df[['definition_id', 'pinyin_id']], 
        on='definition_id', 
        how='left'
    )
    
    # Check for missing pinyin_id
    missing_pinyin = merged_df[merged_df['pinyin_id'].isna()]
    if len(missing_pinyin) > 0:
        print(f"Warning: {len(missing_pinyin)} examples have missing pinyin_id")
        print("These will be assigned the lowest priority (highest frequency_rank)")
    
    # Merge with pinyin data to get frequency_rank
    print("Merging with pinyin data to get frequency ranks...")
    final_df = merged_df.merge(
        pinyin_df[['pinyin_id', 'hanzi', 'frequency_rank']], 
        on='pinyin_id', 
        how='left'
    )
    
    # Check for missing frequency_rank
    missing_freq = final_df[final_df['frequency_rank'].isna()]
    if len(missing_freq) > 0:
        print(f"Warning: {len(missing_freq)} examples have missing frequency_rank")
        print("These will be assigned the lowest priority (frequency_rank = 999999)")
        final_df['frequency_rank'] = final_df['frequency_rank'].fillna(999999)
    
    # Sort by frequency_rank (ascending - lower rank = higher frequency)
    print("Sorting examples by frequency rank...")
    final_df = final_df.sort_values('frequency_rank', ascending=True)
    
    # Reset index to reflect the new order
    final_df = final_df.reset_index(drop=True)
    
    # Add a new column to show the reranked order
    final_df['reranked_order'] = range(1, len(final_df) + 1)
    
    # Select and reorder columns for the output
    output_columns = [
        'reranked_order',
        'definition_id', 
        'example_sn', 
        'example_cn', 
        'example_en', 
        'example_img',
        'pinyin_id',
        'hanzi',
        'frequency_rank'
    ]
    
    output_df = final_df[output_columns]
    
    # Save the reranked examples
    output_path = 'others/hanzi_examples_v7_reranked.csv'
    print(f"Saving reranked examples to {output_path}...")
    output_df.to_csv(output_path, index=False)
    
    # Print summary statistics
    print("\nReranking Summary:")
    print(f"Total examples processed: {len(output_df)}")
    print(f"Examples with frequency_rank 1-100: {len(output_df[output_df['frequency_rank'] <= 100])}")
    print(f"Examples with frequency_rank 101-500: {len(output_df[(output_df['frequency_rank'] > 100) & (output_df['frequency_rank'] <= 500)])}")
    print(f"Examples with frequency_rank 501-1000: {len(output_df[(output_df['frequency_rank'] > 500) & (output_df['frequency_rank'] <= 1000)])}")
    print(f"Examples with frequency_rank > 1000: {len(output_df[output_df['frequency_rank'] > 1000])}")
    
    # Show some examples of the reranking
    print("\nTop 10 most frequent hanzi examples:")
    print(output_df[['reranked_order', 'hanzi', 'example_cn', 'frequency_rank']].head(10).to_string(index=False))
    
    print("\nBottom 10 least frequent hanzi examples:")
    print(output_df[['reranked_order', 'hanzi', 'example_cn', 'frequency_rank']].tail(10).to_string(index=False))
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Rerank hanzi examples by frequency')
    parser.add_argument('--output', '-o', default='database_csv/hanzi_examples_v7_reranked.csv',
                       help='Output file path (default: database_csv/hanzi_examples_v7_reranked.csv)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    output_path = rerank_examples_by_frequency()
    
    print(f"\nReranking completed! Output saved to: {output_path}")
    print("You can now use this reranked file for image generation.")

if __name__ == '__main__':
    main() 