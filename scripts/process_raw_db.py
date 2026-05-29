import sqlite3
import os
import json

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
        
    def get_all_entries(self):
        try:
            self.cursor.execute('SELECT entry, paraphrase FROM mdx')
            result = self.cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    db_file = "raw_data/jjhy_dictionary_raw.db"
    query = SQLiteQuery(db_file)
    # Hanzi
    # entry_keys = ["00004*3500汉字索引*","00005*3501-5500汉字索引*",
    #     "00006*5501-6800汉字索引*","00007*6801-19142汉字索引*"]

    # Cihui
    entry_keys = ["00037*收录词汇——1--5000词索引*","00038*收录词汇——5001--10000词索引*",
        "00039*收录词汇——10001--15000词索引*","00040*收录词汇——15001--20000词索引*",
        "00041*收录词汇——20001--25000词索引*","00042*收录词汇——25001--30000词索引*",
        "00043*收录词汇——30001--35000词索引*","00044*收录词汇——35001--40000词索引*",
        "00045*收录词汇——40001--45000词索引*","00046*收录词汇——45001--50000词索引*",
        "00047*收录词汇——50001--55000词索引*","00048*收录词汇——55001--60000词索引*",
        "00049*收录词汇——60001--65000词索引*","00050*收录词汇——65001--70000词索引*",
        "00051*收录词汇——70001--75000词索引*","00052*收录词汇——75001--80000词索引*",
        "00053*收录词汇——80001--85000词索引*","00054*收录词汇——85001--90000词索引*",
        "00055*收录词汇——90001--95000词索引*"]

    for key in entry_keys:
        value = query.get_paraphrase_by_entry(key)
        # Save all entries to JSON file
        json_path = f"raw_data/jjhy_{key.replace('*', '-')}.html"
        with open(json_path, "w", encoding="utf-8") as f:
            # Convert list of tuples to list of dicts for better JSON structure
            f.write(value[0][0])
        print(f"Saved {json_path}")
    query.close()
