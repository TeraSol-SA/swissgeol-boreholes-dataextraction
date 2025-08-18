#!/usr/bin/env python3
"""Command-line image classifier for borehole profile images."""

import csv
import os
import subprocess
import sys
from pathlib import Path


class CommandLineImageClassifier:
    def __init__(self, image_dir="data/output/draw", output_csv="image_classifications_cli.csv"):
        self.image_dir = Path(image_dir)
        self.output_csv = output_csv
        self.current_index = 0
        
        # Get all image files
        self.image_files = []
        if self.image_dir.exists():
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']:
                self.image_files.extend(self.image_dir.glob(ext))
        
        # Sort files naturally
        self.image_files = sorted(self.image_files, key=self._natural_sort_key)
        self.image_files = [f for f in self.image_files if not f.name.startswith('.')]
        
        if not self.image_files:
            print(f"No images found in {image_dir}")
            return
        
        # Load existing classifications
        self.existing_data = {}
        self._load_existing_classifications()
        
        print(f"Found {len(self.image_files)} images")
        print(f"Already classified: {len(self.existing_data)} images")
        
    def _natural_sort_key(self, filename):
        """Generate a natural sort key for filenames with numbers."""
        import re
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        return [convert(c) for c in re.split(r'(\d+)', str(filename.name))]
    
    def _get_base_filename(self, filename):
        """Extract the base filename without page number."""
        # Examples: 
        # "11709_part2.pdf_page2.png" -> "11709_part2.pdf"
        # "13076.pdf_page1.png" -> "13076.pdf"
        if '_page' in filename:
            return filename.split('_page')[0]
        return filename
    
    def _find_previous_same_document(self, current_filename):
        """Find the most recent classification for the same document."""
        current_base = self._get_base_filename(current_filename)
        
        # Look through already processed files for the same document
        for filename, data in self.existing_data.items():
            if self._get_base_filename(filename) == current_base and filename != current_filename:
                return data
        
        return None
    
    def _load_existing_classifications(self):
        """Load existing classifications from CSV."""
        if os.path.exists(self.output_csv):
            try:
                with open(self.output_csv, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        filename = row['filename']
                        self.existing_data[filename] = {
                            'only_images': int(row['only_images']),
                            'description_quality': int(row['description_quality']),
                            'heights_quality': int(row['heights_quality']),
                            'rotate': int(row.get('rotate', 0))  # Default to 0 if not present
                        }
            except Exception as e:
                print(f"Warning: Could not load existing CSV: {e}")
    
    def _open_image(self, image_path):
        """Open image with the default system viewer."""
        try:
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', str(image_path)], check=True)
            elif sys.platform.startswith('linux'):  # Linux
                subprocess.run(['xdg-open', str(image_path)], check=True)
            elif sys.platform.startswith('win'):  # Windows
                subprocess.run(['start', str(image_path)], shell=True, check=True)
            else:
                print(f"Please manually open: {image_path}")
        except Exception as e:
            print(f"Could not open image automatically: {e}")
            print(f"Please manually open: {image_path}")
    
    def _get_input(self, prompt, valid_values, current_value=None, default_value=0):
        """Get user input with validation."""
        if current_value is not None:
            prompt += f" (current: {current_value}, default: {default_value})"
        else:
            prompt += f" (default: {default_value})"
        
        while True:
            try:
                value = input(f"{prompt}: ").strip()
                
                if value == '':
                    return current_value if current_value is not None else default_value
                
                if value == 'q':
                    return 'quit'
                
                if value == 's':
                    return 'skip'
                
                value = int(value)
                if value in valid_values:
                    return value
                else:
                    print(f"Invalid input. Please enter one of: {valid_values} (or 'q' to quit, 's' to skip, Enter for default)")
            except ValueError:
                print(f"Invalid input. Please enter a number from: {valid_values} (or 'q' to quit, 's' to skip, Enter for default)")
    
    def _save_classification(self, filename, only_images, description_quality, heights_quality, rotate):
        """Save a single classification."""
        self.existing_data[filename] = {
            'only_images': only_images,
            'description_quality': description_quality,
            'heights_quality': heights_quality,
            'rotate': rotate
        }
    
    def _save_all_to_csv(self):
        """Save all classifications to CSV."""
        try:
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['filename', 'only_images', 'description_quality', 'heights_quality', 'rotate']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for filename, data in self.existing_data.items():
                    writer.writerow({
                        'filename': filename,
                        'only_images': data['only_images'],
                        'description_quality': data['description_quality'],
                        'heights_quality': data['heights_quality'],
                        'rotate': data.get('rotate', 0)  # Default to 0 if not present
                    })
            
            print(f"\n✓ Saved {len(self.existing_data)} classifications to {self.output_csv}")
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False
    
    def run(self):
        """Run the command-line classifier."""
        if not self.image_files:
            return
        
        try:
            for i, image_file in enumerate(self.image_files):
                filename = image_file.name
                
                # Skip if already classified (unless user wants to re-classify)
                if filename in self.existing_data:
                    existing = self.existing_data[filename]
                    print(f"\n[{i+1}/{len(self.image_files)}] {filename}")
                    print(f"Already classified: Only Images={existing['only_images']}, "
                          f"Description={existing['description_quality']}, Heights={existing['heights_quality']}")
                    
                    reclassify = input("Re-classify? (y/N): ").strip().lower()
                    if reclassify != 'y':
                        continue
                
                print(f"\n[{i+1}/{len(self.image_files)}] Classifying: {filename}")
                
                # Open the image
                print("Opening image...")
                self._open_image(image_file)
                
                # Get current values if they exist
                current_values = self.existing_data.get(filename, {})
                
                # If no current values, check for previous page from same document
                if not current_values:
                    previous_data = self._find_previous_same_document(filename)
                    if previous_data:
                        current_values = previous_data
                        print(f"Using previous page defaults for {filename}")
                
                # Get classifications
                only_images = self._get_input(
                    "Only Images (0=No, 1=Yes)", 
                    [0, 1], 
                    current_values.get('only_images'),
                    default_value=0
                )
                if only_images == 'quit':
                    break
                elif only_images == 'skip':
                    continue
                
                description_quality = self._get_input(
                    "Description Quality (0-5)", 
                    [0, 1, 2, 3, 4, 5], 
                    current_values.get('description_quality'),
                    default_value=0
                )
                if description_quality == 'quit':
                    break
                elif description_quality == 'skip':
                    continue
                
                heights_quality = self._get_input(
                    "Heights Quality (0-5)", 
                    [0, 1, 2, 3, 4, 5], 
                    current_values.get('heights_quality'),
                    default_value=0
                )
                if heights_quality == 'quit':
                    break
                elif heights_quality == 'skip':
                    continue
                
                rotate = self._get_input(
                    "Rotate (0=No, 1=Yes)", 
                    [0, 1], 
                    current_values.get('rotate'),
                    default_value=0
                )
                if rotate == 'quit':
                    break
                elif rotate == 'skip':
                    continue
                
                # Save classification
                self._save_classification(filename, only_images, description_quality, heights_quality, rotate)
                print(f"✓ Saved classification for {filename}")
                
                # Auto-save every 10 classifications
                if len(self.existing_data) % 10 == 0:
                    self._save_all_to_csv()
                    print("Auto-saved progress...")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Saving progress...")
        
        # Final save
        self._save_all_to_csv()
        print(f"\nClassification session complete!")
        print(f"Total classified: {len(self.existing_data)} images")


def main():
    """Main function."""
    import sys
    
    image_dir = "data/output/draw"
    output_csv = "image_classifications_cli.csv"
    
    if len(sys.argv) > 1:
        image_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_csv = sys.argv[2]
    
    classifier = CommandLineImageClassifier(image_dir, output_csv)
    classifier.run()


if __name__ == "__main__":
    main()
