import glob
import os
import csv
import re

from jjhy_tool_parse_html import extract_hanzi_cihui_entries
from process_raw_db import SQLiteQuery

TAG = "cihui"
INPUT_PATTERN = f"others/jjhy_{TAG}_frequency_rank_*.csv"
DB_PATH = "raw_data/xdhygf_dictionary_v2.db"
OUTPUT_TEMPLATE = f"others/jjhy_{TAG}_parsed_{{suffix}}.csv"

def main():
    db = SQLiteQuery(DB_PATH)
    for input_path in glob.glob(INPUT_PATTERN):
        suffix = os.path.basename(input_path).replace(f"jjhy_{TAG}_frequency_rank_", "")
        suffix = suffix.replace(".csv", "")
        output_path = OUTPUT_TEMPLATE.format(suffix=suffix)
        print(f"Processing {input_path} -> {output_path}")
        with open(input_path, newline='', encoding='utf-8') as infile, \
             open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.DictReader(infile)
            fieldnames = ["rank", f"{TAG}", "pinyin", "ref_hanzi", "ref_pinyin",  "pos", "definition", "example"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                rank = row["rank"]
                hanzi = row[TAG]
                is_hanzi = re.match(r'^[一-龯,，]+$', hanzi) is not None
                if not is_hanzi:
                    # set color to yellow
                    print(f"\033[93mNot a hanzi: {rank} - {hanzi}\033[0m")
                    continue
                db_result = db.get_paraphrase_by_entry(hanzi)
                if not db_result:
                    # set color to red
                    # print(f"\033[91mNo html result for {rank} - {hanzi}\033[0m")
                    continue
                html = db_result[0][0]
                entries = extract_hanzi_cihui_entries(html)
                if not entries:
                    raise Exception(f"No parsed entries for {rank} - {hanzi}: {html}")

                for entry in entries:
                    # Only match the exact hanzi
                    if entry["hanzi"] != hanzi:
                        print(f"Hanzi {entry['hanzi']} mismatch for {rank} - {hanzi}")
                        continue
                    pinyin = entry["pinyin"]
                    for sense in entry["senses"]:
                        pos = sense["pos"] or ""
                        definition = sense["definition"] or ""
                        examples = sense["examples"] or [""]
                        words = entry["words"] if "words" in entry else []
                        ref_word = ""
                        origin_pinyin  = pinyin
                        ref_pinyin = ""
                        if words and len(words) > 1:
                            ref_word = words[1]
                            origin_pinyin = pinyin[0]
                            ref_pinyin = pinyin[1]
                        for example in examples:
                            writer.writerow({
                                "rank": rank,
                                TAG: hanzi,
                                "pinyin": origin_pinyin,
                                "ref_hanzi": ref_word,
                                "ref_pinyin": ref_pinyin,
                                "pos": pos,
                                "definition": definition,
                                "example": example
                            })
    db.close()

if __name__ == "__main__":
    main()










