import glob
import os
import csv

from process_raw_db import SQLiteQuery

TAG = "hanzi"
INPUT_PATTERN = f"jjhy_csv/tofixdefinition/jjhy_{TAG}_parsed_*_filtered.csv"
DB_PATH = "raw_data/xdhygf_dictionary_v2.db"
OUTPUT_TEMPLATE = f"jjhy_csv/tofixdefinition/jjhy_{TAG}_html_{{suffix}}.csv"

def main():
    db = SQLiteQuery(DB_PATH)
    total_rows = 0
    total_html_chars = 0
    for input_path in glob.glob(INPUT_PATTERN):
        suffix = os.path.basename(input_path).replace(f"jjhy_{TAG}_parsed_", "")
        suffix = suffix.replace("_filtered.csv", "")
        output_path = OUTPUT_TEMPLATE.format(suffix=suffix)
        print(f"Processing {input_path} -> {output_path}")
        with open(input_path, newline='', encoding='utf-8') as infile, \
             open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.DictReader(infile)
            # fieldnames = ["rank", f"{TAG}", "pinyin", "ref_hanzi", "ref_pinyin",  "pos", "definition", "example"]
            fieldnames = ["rank", f"{TAG}", "pinyin", "raw_html"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                rank = row["rank"]
                hanzi = row[TAG]
                pinyin = row["pinyin"]
                db_result = db.get_paraphrase_by_entry(hanzi)
                if not db_result:
                    # set color to red
                    # print(f"\033[91mNo html result for {rank} - {hanzi}\033[0m")
                    continue
                html = db_result[0][0]
                
                writer.writerow({
                            "rank": rank,
                            TAG: hanzi,
                            "pinyin": pinyin,
                            "raw_html": html
                        })                    
                total_rows += 1
                total_html_chars += len(html)

    print(f"Total rows: {total_rows}")
    print(f"Total html chars: {total_html_chars}")
    db.close()

if __name__ == "__main__":
    main()










