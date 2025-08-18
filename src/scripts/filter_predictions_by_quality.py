#!/usr/bin/env python3
"""
Filter predictions.json to keep only PDFs with perfect quality scores (5/5).

This script reads the image_classifications.csv file to identify PDFs that have
both description_quality=5 and heights_quality=5, then filters the predictions.json
file to keep only those entries.
"""

import json
import csv
import os
from pathlib import Path

def read_classifications(csv_path):
    """Read the image classifications CSV and identify perfect score PDFs."""
    perfect_score_pdfs = set()
    
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check if both description_quality and heights_quality are 5
            if (row['description_quality'] == '5' and 
                row['heights_quality'] == '5'):
                # Extract PDF name from filename (remove _pageX.png)
                filename = row['filename']
                if filename.endswith('.png'):
                    # Remove .png extension
                    filename = filename[:-4]
                    # Remove page suffix (e.g., _page1, _page2, etc.)
                    if '_page' in filename:
                        pdf_name = filename.rsplit('_page', 1)[0]
                        # Add .pdf extension only if it doesn't already have it
                        if not pdf_name.endswith('.pdf'):
                            pdf_name += '.pdf'
                    else:
                        pdf_name = filename
                        if not pdf_name.endswith('.pdf'):
                            pdf_name += '.pdf'
                    perfect_score_pdfs.add(pdf_name)
    
    return perfect_score_pdfs

def filter_predictions(json_path, perfect_score_pdfs):
    """Filter predictions.json to keep only perfect score PDFs."""
    with open(json_path, 'r', encoding='utf-8') as f:
        predictions = json.load(f)
    
    # Filter to keep only perfect score PDFs
    filtered_predictions = {
        pdf_name: data 
        for pdf_name, data in predictions.items() 
        if pdf_name in perfect_score_pdfs
    }
    
    return filtered_predictions

def main():
    # Define file paths
    base_dir = Path(__file__).parent.parent.parent
    csv_path = base_dir / 'image_classifications.csv'
    json_path = base_dir / 'data' / 'output' / 'predictions.json'
    output_path = base_dir / 'data' / 'output' / 'predictions_filtered.json'
    
    # Check if files exist
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return
    
    if not json_path.exists():
        print(f"Error: JSON file not found at {json_path}")
        return
    
    print("Reading image classifications...")
    perfect_score_pdfs = read_classifications(csv_path)
    print(f"Found {len(perfect_score_pdfs)} PDFs with perfect scores (5/5):")
    for pdf in sorted(perfect_score_pdfs):
        print(f"  - {pdf}")
    
    print("\nFiltering predictions.json...")
    filtered_predictions = filter_predictions(json_path, perfect_score_pdfs)
    
    print(f"Original predictions.json had {len(json.load(open(json_path)))} entries")
    print(f"Filtered predictions will have {len(filtered_predictions)} entries")
    
    # Save filtered predictions
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_predictions, f, ensure_ascii=False, indent=2)
    
    print(f"\nFiltered predictions saved to: {output_path}")
    
    # Show which PDFs were kept
    print("\nKept PDFs:")
    for pdf_name in sorted(filtered_predictions.keys()):
        print(f"  - {pdf_name}")

if __name__ == "__main__":
    main()
