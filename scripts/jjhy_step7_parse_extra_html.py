import glob
import os
import csv
import re

from jjhy_tool_parse_html import extract_hanzi_cihui_entries
from process_raw_db import SQLiteQuery

TAG = "hanzi"
INPUT_PATTERN = f"others/jjhy_{TAG}_frequency_rank_*.csv"
DB_PATH = "raw_data/xdhygf_dictionary_v2.db"
# OUTPUT_TEMPLATE = f"others/jjhy_{TAG}_parsed_{{suffix}}.csv"
OUTPUT_TEMPLATE = f"others/jjhy_{TAG}_invalid_parsed_{{suffix}}.csv"

def main():
    db = SQLiteQuery(DB_PATH)
    total_rows = 0
    total_html_chars = 0
    total_mismatch_parsed = 0
    total_invalid_parsed = 0
    total_has_subdefs = 0
    for input_path in glob.glob(INPUT_PATTERN):
        suffix = os.path.basename(input_path).replace(f"jjhy_{TAG}_frequency_rank_", "")
        suffix = suffix.replace(".csv", "")
        output_path = OUTPUT_TEMPLATE.format(suffix=suffix)
        print(f"Processing {input_path} -> {output_path}")
        with open(input_path, newline='', encoding='utf-8') as infile, \
             open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.DictReader(infile)
            # fieldnames = ["rank", f"{TAG}", "pinyin", "ref_hanzi", "ref_pinyin",  "pos", "definition", "example"]
            fieldnames = ["rank", f"{TAG}", "pinyin", "mismatch_parsed", "invalid_parsed", "has_subdefs", "raw_html"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                rank = row["rank"]
                hanzi = row[TAG]
                is_hanzi = re.match(r'^[一-龯,，]+$', hanzi) is not None
                if not is_hanzi:
                    # set color to yellow
                    # print(f"\033[93mNot a hanzi: {rank} - {hanzi}\033[0m")
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

                has_subdefs = html.find("<x-a>") != -1
                mismatch_parsed = False
                invalid_parsed = False
                for index, entry in enumerate(entries):
                    # Only match the exact hanzi
                    if entry["hanzi"] != hanzi:
                        print(f"Hanzi {entry['hanzi']} mismatch for {rank} - {hanzi}")
                        mismatch_parsed = True
                        # continue
                    pinyin = entry["pinyin"]
                    senses = entry["senses"] or []
                    if len(senses) == 0:
                        # print(f"No senses for {rank} - {index}- {hanzi}")
                        invalid_parsed = True
                        break
                
                writer.writerow({
                            "rank": rank,
                            TAG: hanzi,
                            "pinyin": pinyin,
                            "mismatch_parsed": mismatch_parsed,
                            "invalid_parsed": invalid_parsed,
                            "has_subdefs": has_subdefs,
                            "raw_html": html
                        })                    
                total_rows += 1
                total_html_chars += len(html)
                total_mismatch_parsed += mismatch_parsed
                total_invalid_parsed += invalid_parsed
                total_has_subdefs += has_subdefs
    print(f"Total rows: {total_rows}")
    print(f"Total html chars: {total_html_chars}")
    print(f"Total mismatch parsed: {total_mismatch_parsed}")
    print(f"Total invalid parsed: {total_invalid_parsed}")
    print(f"Total has subdefs: {total_has_subdefs}")
    db.close()

if __name__ == "__main__":
    main()










