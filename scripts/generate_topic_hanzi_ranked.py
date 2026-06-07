#!/usr/bin/env python3
"""
Generate a new CSV with structure: id, topic, hanzi, frequency_rank

Reads hanzi_topic_words_strict.csv for topic-hanzi mappings, looks up frequency_rank
from jjhy_core_hanzi_pinyin.csv. Within each topic, sorts hanzi by frequency_rank ascending,
then assigns sequential ids starting from 4916.
"""

import pandas as pd
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOPIC_FILE = os.path.join(PROJECT_ROOT, "jjhy_csv", "topic", "hanzi_topic_words_strict.csv")
PINYIN_FILE = os.path.join(PROJECT_ROOT, "live_data", "jjhy_core_hanzi_pinyin.csv")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "jjhy_csv", "topic", "hanzi_topic_words_ranked.csv")

ID_START = 4916


def main():
    # 1. Read topic-hanzi mappings
    topic_df = pd.read_csv(TOPIC_FILE)
    print(f"Read {len(topic_df)} rows from topic file")

    # 2. Read pinyin file and build hanzi -> frequency_rank map
    #    (each hanzi has the same frequency_rank across all pinyin rows, take first)
    pinyin_df = pd.read_csv(PINYIN_FILE)
    hanzi_rank = pinyin_df.groupby("hanzi")["frequency_rank"].first().to_dict()
    print(f"Built frequency_rank map for {len(hanzi_rank)} unique hanzi")

    # 3. Look up frequency_rank for each hanzi in topic
    topic_df["frequency_rank"] = topic_df["hanzi"].map(hanzi_rank)

    # Check for missing
    missing = topic_df[topic_df["frequency_rank"].isna()]
    if len(missing) > 0:
        print(f"WARNING: {len(missing)} hanzi not found in pinyin file:")
        for _, row in missing.iterrows():
            print(f"  - {row['hanzi']} (topic: {row['topic']})")

    # 4. Preserve original topic order, sort hanzi within each topic by frequency_rank ascending
    topic_order = topic_df["topic"].drop_duplicates().tolist()
    topic_df["topic"] = pd.Categorical(topic_df["topic"], categories=topic_order, ordered=True)
    topic_df = topic_df.sort_values(["topic", "frequency_rank"], ascending=[True, True])

    # 5. Assign sequential ids starting from ID_START
    topic_df = topic_df.reset_index(drop=True)
    topic_df["id"] = range(ID_START, ID_START + len(topic_df))

    # 6. Reorder and output
    output_df = topic_df[["id", "topic", "hanzi", "frequency_rank"]]
    output_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(output_df)} rows to: {OUTPUT_FILE}")
    print(f"ID range: {ID_START} to {ID_START + len(output_df) - 1}")
    print(f"Unique topics: {output_df['topic'].nunique()}")


if __name__ == "__main__":
    main()
