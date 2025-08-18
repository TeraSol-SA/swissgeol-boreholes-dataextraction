#!/usr/bin/env python3
"""Simple script to list all filenames in data/output/draw folder and export to CSV."""

import csv
import os
import re
from pathlib import Path


def natural_sort_key(filename):
    """
    Generate a key for natural sorting (treats numbers as numbers, not strings).
    This makes '9156.pdf' come before '11084.pdf' as expected.
    """
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    
    return [convert(c) for c in re.split(r'(\d+)', filename)]


def list_files_to_csv(input_dir="data/output/draw", output_file="filenames.csv", sort_method="natural"):
    """
    Read all filenames from the specified directory and write them to a CSV file.
    
    Args:
        input_dir (str): Directory to scan for files
        output_file (str): Output CSV filename
        sort_method (str): Sorting method - "natural", "alphabetical", "none", or "modification_time"
    """
    # Get the directory path
    dir_path = Path(input_dir)
    
    if not dir_path.exists():
        print(f"Error: Directory '{input_dir}' does not exist!")
        return
    
    # Get all files in the directory
    files = []
    for item in dir_path.iterdir():
        if item.is_file() and not item.name.startswith('.'):  # Skip hidden files like .DS_Store
            files.append(item.name)
    
    # Sort files based on the chosen method
    if sort_method == "natural":
        files.sort(key=natural_sort_key)
        print(f"✓ Sorted files using natural sorting (numbers treated as numbers)")
    elif sort_method == "alphabetical":
        files.sort()
        print(f"✓ Sorted files alphabetically")
    elif sort_method == "modification_time":
        files.sort(key=lambda f: (dir_path / f).stat().st_mtime)
        print(f"✓ Sorted files by modification time")
    elif sort_method == "none":
        print(f"✓ Files listed in directory order (no sorting)")
    else:
        print(f"Warning: Unknown sort method '{sort_method}', using natural sorting")
        files.sort(key=natural_sort_key)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['filename'])
        
        # Write each filename as a row
        for filename in files:
            writer.writerow([filename])
    
    print(f"✓ Found {len(files)} files in '{input_dir}'")
    print(f"✓ Exported filenames to '{output_file}'")


if __name__ == "__main__":
    import sys
    
    # Check command line arguments for sorting method
    if len(sys.argv) > 1:
        sort_method = sys.argv[1]
        if sort_method not in ["natural", "alphabetical", "none", "modification_time"]:
            print("Usage: python list_files_to_csv.py [natural|alphabetical|none|modification_time]")
            print("  natural: Numbers treated as numbers (9156 before 11084)")
            print("  alphabetical: Standard string sorting")
            print("  none: No sorting, directory order")
            print("  modification_time: Sort by file modification time")
            sys.exit(1)
    else:
        sort_method = "natural"  # Default to natural sorting
    
    # Run the function
    list_files_to_csv(sort_method=sort_method)
    
    print(f"\nTo try different sorting methods:")
    print(f"  python {sys.argv[0]} natural")
    print(f"  python {sys.argv[0]} alphabetical") 
    print(f"  python {sys.argv[0]} none")
    print(f"  python {sys.argv[0]} modification_time")
