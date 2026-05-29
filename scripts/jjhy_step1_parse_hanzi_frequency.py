#!/usr/bin/env python3
"""
Script to parse hanzi frequency data from HTML file.
Extracts hanzi characters and their frequency rank numbers.
"""

import re
import csv
import sys
from pathlib import Path


def parse_hanzi_frequency(html_file_path):
    """
    Parse the HTML file to extract hanzi characters and their frequency rank numbers.
    
    Args:
        html_file_path (str): Path to the HTML file
        
    Returns:
        list: List of tuples containing (rank, hanzi) pairs
    """
    hanzi_data = []
    
    # Regular expression to match the pattern: rank_number + tab + <A HREF="entry://hanzi">hanzi</a>
    pattern = r'^(\d{5})\t<A HREF="entry://([^"]+)">\2</a>$'
    # Sometimes the pattern is like this: 19102	㴔
    pattern2 = r'^(\d{5})\t([^\t]+)$'
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                match = re.match(pattern, line)
                if match:
                    rank = int(match.group(1))
                    hanzi = match.group(2)
                    hanzi_data.append((rank, hanzi))
                elif re.match(pattern2, line):
                    rank = int(match.group(1))
                    hanzi = match.group(2)
                    hanzi_data.append((rank, hanzi))
                else:
                    # Skip lines that don't match the pattern (headers, etc.)
                    continue
                    
    except FileNotFoundError:
        print(f"Error: File '{html_file_path}' not found.")
        return []
    except UnicodeDecodeError:
        print(f"Error: Unable to decode file '{html_file_path}' with UTF-8 encoding.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    return hanzi_data


def save_to_csv(hanzi_data, output_file_path):
    """
    Save the hanzi frequency data to a CSV file.
    
    Args:
        hanzi_data (list): List of tuples containing (rank, hanzi) pairs
        output_file_path (str): Path to the output CSV file
    """
    try:
        with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['rank', 'hanzi'])
            # Write data
            for rank, hanzi in hanzi_data:
                writer.writerow([rank, hanzi])
        print(f"Successfully saved {len(hanzi_data)} hanzi entries to '{output_file_path}'")
    except Exception as e:
        print(f"Error saving CSV file: {e}")


def print_summary(hanzi_data):
    """
    Print a summary of the parsed data.
    
    Args:
        hanzi_data (list): List of tuples containing (rank, hanzi) pairs
    """
    if not hanzi_data:
        print("No hanzi data found.")
        return
    
    print(f"\nSummary:")
    print(f"Total hanzi characters: {len(hanzi_data)}")
    print(f"Rank range: {hanzi_data[0][0]} - {hanzi_data[-1][0]}")
    
    # Show first 10 entries
    print(f"\nFirst 10 entries:")
    for rank, hanzi in hanzi_data[:10]:
        print(f"  {rank:05d}: {hanzi}")
    
    # Show last 10 entries
    print(f"\nLast 10 entries:")
    for rank, hanzi in hanzi_data[-10:]:
        print(f"  {rank:05d}: {hanzi}")


def main():
    """Main function to run the script."""
    # Default file paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    html_file = project_root / "raw_data" / "jjhy_00006-5501-6800汉字索引-.html"
    output_file = project_root / "others" / "jjhy_hanzi_frequency_rank_6800.csv"
    
    # Check if input file exists
    if not html_file.exists():
        print(f"Error: HTML file not found at '{html_file}'")
        print("Please make sure the file exists in the raw_data directory.")
        sys.exit(1)
    
    print(f"Parsing hanzi frequency data from: {html_file}")
    
    # Parse the HTML file
    hanzi_data = parse_hanzi_frequency(html_file)
    
    if not hanzi_data:
        print("No hanzi data extracted. Please check the HTML file format.")
        sys.exit(1)
    
    # Print summary
    print_summary(hanzi_data)
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    save_to_csv(hanzi_data, output_file)
    
    print(f"\nParsing completed successfully!")
    print(f"Output saved to: {output_file}")


if __name__ == "__main__":
    main() 