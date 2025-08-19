#!/usr/bin/env python3
"""
Filter predictions.json to keep only PDFs with perfect quality scores (5/5).

This script reads the image_classifications.csv file to identify PDFs that have
both description_quality=5 and heights_quality=5, then filters the predictions.json
file to keep only those entries. It also copies the corresponding input PDFs and
output PNG images to organized filtered directories.
"""

import json
import csv
import os
import shutil
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

def copy_input_pdfs(perfect_score_pdfs, input_dir, output_dir):
    """Copy input PDFs with perfect scores to filtered directory."""
    copied_pdfs = []
    skipped_pdfs = []
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for pdf_name in perfect_score_pdfs:
        source_path = input_dir / pdf_name
        dest_path = output_dir / pdf_name
        
        if source_path.exists():
            try:
                shutil.copy2(source_path, dest_path)
                copied_pdfs.append(pdf_name)
                print(f"  ✓ Copied: {pdf_name}")
            except Exception as e:
                print(f"  ✗ Error copying {pdf_name}: {e}")
                skipped_pdfs.append(pdf_name)
        else:
            print(f"  ✗ Not found: {pdf_name}")
            skipped_pdfs.append(pdf_name)
    
    return copied_pdfs, skipped_pdfs

def copy_output_images(perfect_score_pdfs, csv_path, draw_dir, output_dir):
    """Copy output PNG images with perfect scores to filtered directory."""
    copied_images = []
    skipped_images = []
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read CSV to get all perfect score image filenames
    perfect_score_images = set()
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if (row['description_quality'] == '5' and 
                row['heights_quality'] == '5'):
                perfect_score_images.add(row['filename'])
    
    # Copy the images
    for image_name in perfect_score_images:
        source_path = draw_dir / image_name
        dest_path = output_dir / image_name
        
        if source_path.exists():
            try:
                shutil.copy2(source_path, dest_path)
                copied_images.append(image_name)
                print(f"  ✓ Copied: {image_name}")
            except Exception as e:
                print(f"  ✗ Error copying {image_name}: {e}")
                skipped_images.append(image_name)
        else:
            print(f"  ✗ Not found: {image_name}")
            skipped_images.append(image_name)
    
    return copied_images, skipped_images

def main():
    # Define file paths
    base_dir = Path(__file__).parent.parent.parent
    csv_path = base_dir / 'image_classifications.csv'
    json_path = base_dir / 'data' / 'output' / 'predictions.json'
    output_path = base_dir / 'data' / 'output' / 'predictions_filtered.json'
    
    # Define input and output directories
    input_dir = base_dir / 'data' / 'input'
    draw_dir = base_dir / 'data' / 'output' / 'draw'
    
    # Define filtered output directories
    filtered_base_dir = base_dir / 'data' / 'output' / 'filtered'
    filtered_input_dir = filtered_base_dir / 'input'
    filtered_draw_dir = filtered_base_dir / 'draw'
    
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
    
    # Copy input PDFs
    print(f"\nCopying input PDFs to {filtered_input_dir}...")
    copied_pdfs, skipped_pdfs = copy_input_pdfs(perfect_score_pdfs, input_dir, filtered_input_dir)
    
    # Copy output images
    print(f"\nCopying output images to {filtered_draw_dir}...")
    copied_images, skipped_images = copy_output_images(perfect_score_pdfs, csv_path, draw_dir, filtered_draw_dir)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Filtered predictions: {len(filtered_predictions)} entries")
    print(f"Copied input PDFs: {len(copied_pdfs)}")
    print(f"Copied output images: {len(copied_images)}")
    
    if skipped_pdfs:
        print(f"Skipped PDFs: {len(skipped_pdfs)}")
        for pdf in skipped_pdfs:
            print(f"  - {pdf}")
    
    if skipped_images:
        print(f"Skipped images: {len(skipped_images)}")
        for image in skipped_images[:5]:  # Show first 5
            print(f"  - {image}")
        if len(skipped_images) > 5:
            print(f"  ... and {len(skipped_images) - 5} more")
    
    # Show directory structure
    print(f"\nOutput structure:")
    print(f"  {output_path}")
    print(f"  {filtered_input_dir}/ ({len(copied_pdfs)} PDFs)")
    print(f"  {filtered_draw_dir}/ ({len(copied_images)} images)")
    
    # Show which PDFs were kept
    print(f"\nKept PDFs:")
    for pdf_name in sorted(filtered_predictions.keys()):
        status = "✓" if pdf_name in [p for p in copied_pdfs] else "✗"
        print(f"  {status} {pdf_name}")

if __name__ == "__main__":
    main()
    