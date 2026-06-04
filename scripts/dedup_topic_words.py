#!/usr/bin/env python3
"""对 hanzi_topic_words_llm.csv 按 (topic, hanzi) 去重。"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPIC_CSV = os.path.join(BASE_DIR, "jjhy_csv", "topic", "hanzi_topic_words_llm.csv")


def main():
    df = pd.read_csv(TOPIC_CSV)

    before = len(df)
    print(f"去重前行数: {before}")

    # 按 topic + hanzi 去重，保留第一次出现的行
    df_dedup = df.drop_duplicates(subset=["topic", "hanzi"], keep="first")
    after = len(df_dedup)
    removed = before - after
    print(f"去重后行数: {after}（移除 {removed} 行重复）")

    df_dedup.to_csv(TOPIC_CSV, index=False)
    print(f"已写回: {TOPIC_CSV}")


if __name__ == "__main__":
    main()
