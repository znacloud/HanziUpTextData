import sqlite3
import os


class SQLiteQuery:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def get_paraphrase_by_entry(self, entry_value):
        try:
            self.cursor.execute('SELECT paraphrase FROM mdx WHERE entry = ?', (entry_value,))
            result = self.cursor.fetchall()
            if result:
                return result
            else:
                return None
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return None

    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    db_file = "raw_data/jjhy_dictionary_raw.db"
    out_dir = "raw_data"
    os.makedirs(out_dir, exist_ok=True)

    query = SQLiteQuery(db_file)

    # Keys from 00065*现代汉语分类大词典索引01* to ...29*
    for idx in range(1, 30):
        key = f"00065*现代汉语分类大词典索引{idx:02d}*"
        value = query.get_paraphrase_by_entry(key)
        out_path = os.path.join(out_dir, f"jjhy-hanzi-topics-{idx:02d}.html")
        if value and len(value) > 0 and len(value[0]) > 0:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(value[0][0])
            print(f"Saved index {idx:02d} -> {out_path}")
        else:
            print(f"No content found for index {idx:02d}")

    query.close()


