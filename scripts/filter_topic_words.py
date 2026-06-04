#!/usr/bin/env python3
"""过滤 hanzi_topic_words_llm.csv，只保留 hanzi 存在于 jjhy_core_hanzi_pinyin.csv 中的行。"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOPIC_CSV = os.path.join(BASE_DIR, "jjhy_csv", "topic", "hanzi_topic_words_strict.csv")
CORE_CSV = os.path.join(BASE_DIR, "live_data", "jjhy_core_hanzi_pinyin.csv")


def main():
    # 读取两个 csv
    topic_df = pd.read_csv(TOPIC_CSV)
    core_df = pd.read_csv(CORE_CSV, usecols=["hanzi"])

    # 获取合法的 hanzi 集合
    valid_hanzi_set = set(core_df["hanzi"].unique())

    print(f"合法 hanzi 数量: {len(valid_hanzi_set)}")
    print(f"过滤前 topic 行数: {len(topic_df)}")

    # 过滤
    before = len(topic_df)
    filtered_df = topic_df[topic_df["hanzi"].isin(valid_hanzi_set)]
    after = len(filtered_df)
    removed = before - after
    print(f"过滤后 topic 行数: {after}（移除 {removed} 行）")

    # 如果存在被移除的行，打印出来
    if removed > 0:
        removed_rows = topic_df[~topic_df["hanzi"].isin(valid_hanzi_set)]
        print(f"被移除的 hanzi: {list(removed_rows['hanzi'].unique())}")

    # 写回原文件
    filtered_df.to_csv(TOPIC_CSV, index=False)
    print(f"已写回: {TOPIC_CSV}")


if __name__ == "__main__":
    main()
