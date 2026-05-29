# JJHY CSV Filtering Summary Report

## Overview
This report summarizes the results of filtering JJHY CSV files based on whether the hanzi/cihui exists in reference files:
- HSK word list (`raw_data/hsk_word.csv`)
- Modern Chinese vocabulary list (`raw_data/现代汉语常用词表_2008_sorted.csv`)

## Reference Data Loaded
- **HSK unique cihui**: 4,993
- **Modern Chinese unique cihui**: 55,735
- **Total unique reference cihui**: 55,772

## Processing Results

### Successfully Processed Files (22/22) ✅
| File | Original Rows | Filtered Rows | Retention Rate | Type |
|------|---------------|---------------|----------------|------|
| jjhy_cihui_parsed_5000_filtered.csv | 6,851 | 6,689 | 97.6% | Cihui |
| jjhy_cihui_parsed_10000_filtered.csv | 5,807 | 5,548 | 95.5% | Cihui |
| jjhy_cihui_parsed_15000_filtered.csv | 5,383 | 5,050 | 93.8% | Cihui |
| jjhy_cihui_parsed_20000_filtered.csv | 5,118 | 4,747 | 92.8% | Cihui |
| jjhy_cihui_parsed_25000_filtered.csv | 4,809 | 4,428 | 92.1% | Cihui |
| jjhy_cihui_parsed_30000_filtered.csv | 4,618 | 4,195 | 90.8% | Cihui |
| jjhy_cihui_parsed_35000_filtered.csv | 4,464 | 3,998 | 89.6% | Cihui |
| jjhy_cihui_parsed_40000_filtered.csv | 4,279 | 3,786 | 88.5% | Cihui |
| jjhy_cihui_parsed_45000_filtered.csv | 4,070 | 3,517 | 86.4% | Cihui |
| jjhy_cihui_parsed_50000_filtered.csv | 4,016 | 3,410 | 84.9% | Cihui |
| jjhy_cihui_parsed_55000_filtered.csv | 3,762 | 3,085 | 82.0% | Cihui |
| jjhy_cihui_parsed_60000_filtered.csv | 3,636 | 2,842 | 78.2% | Cihui |
| jjhy_cihui_parsed_65000_filtered.csv | 3,426 | 2,548 | 74.4% | Cihui |
| jjhy_cihui_parsed_70000_filtered.csv | 3,261 | 2,219 | 68.0% | Cihui |
| jjhy_cihui_parsed_75000_filtered.csv | 2,966 | 1,739 | 58.6% | Cihui |
| jjhy_cihui_parsed_80000_filtered.csv | 2,769 | 1,256 | 45.4% | Cihui |
| jjhy_cihui_parsed_85000_filtered.csv | 2,418 | 700 | 28.9% | Cihui |
| jjhy_cihui_parsed_90000_filtered.csv | 2,340 | 328 | 14.0% | Cihui |
| jjhy_cihui_parsed_95000_filtered.csv | 1,160 | 78 | 6.7% | Cihui |
| **jjhy_hanzi_parsed_3500_filtered.csv** | **12,852** | **11,205** | **87.2%** | **Hanzi** |
| **jjhy_hanzi_parsed_5500_filtered.csv** | **2,511** | **407** | **16.2%** | **Hanzi** |
| **jjhy_hanzi_parsed_6800_filtered.csv** | **1,446** | **63** | **4.4%** | **Hanzi** |

## Summary Statistics
- **Total files processed**: 22 ✅
- **Successfully processed**: 22 (100%)
- **Failed to process**: 0 (0%)
- **Total original rows**: 91,962
- **Total filtered rows**: 71,838
- **Overall retention rate**: 78.1%

## Output Location
All successfully filtered files have been saved to: `jjhy_csv/core_csv/`

## Key Insights

### Cihui Files (19 files)
- **Retention range**: 97.6% to 6.7%
- **Pattern**: Higher-ranked files (lower numbers) have higher retention rates
- **Top performers**: 5000, 10000, 15000 ranked files with >90% retention
- **Lower performers**: 85000, 90000, 95000 ranked files with <30% retention

### Hanzi Files (3 files) - Now Successfully Processed! ✅
- **jjhy_hanzi_parsed_3500_filtered.csv**: 87.2% retention (11,205/12,852 rows)
- **jjhy_hanzi_parsed_5500_filtered.csv**: 16.2% retention (407/2,511 rows)  
- **jjhy_hanzi_parsed_6800_filtered.csv**: 4.4% retention (63/1,446 rows)

### Overall Performance
- **Cihui files**: Average retention ~75%
- **Hanzi files**: Average retention ~36%
- **Combined**: 78.1% overall retention rate

## Notes
1. **All files now processed successfully** after fixing CSV parsing issues
2. **Cihui files** consistently show higher retention rates, indicating they contain more standard vocabulary
3. **Hanzi files** show lower retention rates, suggesting they contain more specialized or less common characters
4. **The filtering successfully creates a comprehensive core vocabulary set** from both cihui and hanzi data
5. **Higher-ranked files** contain more essential, commonly-used vocabulary that appears in standard reference lists

## Recommendations
1. ✅ **CSV parsing issues resolved** - All files now process successfully
2. **The filtering system works effectively** for both cihui and hanzi data types
3. **Consider the retention patterns** when using the filtered data:
   - Use higher-ranked files for core vocabulary
   - Use lower-ranked files for specialized vocabulary
4. **The core_csv directory now contains a complete, filtered dataset** ready for further analysis or use
