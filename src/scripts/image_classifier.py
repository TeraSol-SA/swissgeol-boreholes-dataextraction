#!/usr/bin/env python3
"""Interactive image classifier for borehole profile images."""

import csv
import os
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image, ImageTk


class ImageClassifier:
    """GUI application for classifying borehole profile images."""
    
    def __init__(self, image_dir="data/output/draw", output_csv="image_classifications.csv"):
        self.image_dir = Path(image_dir)
        self.output_csv = output_csv
        self.current_index = 0
        self.classifications = []
        
        # Get all image files
        self.image_files = []
        if self.image_dir.exists():
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']:
                self.image_files.extend(self.image_dir.glob(ext))
        
        # Sort files naturally (numbers as numbers)
        self.image_files = sorted(self.image_files, key=self._natural_sort_key)
        
        # Filter out hidden files
        self.image_files = [f for f in self.image_files if not f.name.startswith('.')]
        
        if not self.image_files:
            messagebox.showerror("Error", f"No images found in {image_dir}")
            return
        
        # Load existing classifications if CSV exists
        self._load_existing_classifications()
        
        # Setup GUI
        self.root = tk.Tk()
        self.root.title("Image Classifier - Borehole Profiles")
        self.root.geometry("1400x900")  # Wider window for side-by-side layout
        
        self._setup_gui()
        self._load_current_image()
        
    def _natural_sort_key(self, filename):
        """Generate a natural sort key for filenames with numbers."""
        import re
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        return [convert(c) for c in re.split('([0-9]+)', str(filename))]
    
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
        
        # Extract current page number for comparison
        current_page_num = 0
        if '_page' in current_filename:
            try:
                current_page_num = int(current_filename.split('_page')[1].split('.')[0])
            except (ValueError, IndexError):
                current_page_num = 0
        
        # Find all pages from the same document with lower page numbers
        candidates = []
        for filename, data in self.existing_data.items():
            if self._get_base_filename(filename) == current_base and filename != current_filename:
                # Extract page number
                page_num = 0
                if '_page' in filename:
                    try:
                        page_num = int(filename.split('_page')[1].split('.')[0])
                    except (ValueError, IndexError):
                        page_num = 0
                
                # Only consider previous pages (lower page numbers)
                if page_num < current_page_num:
                    candidates.append((page_num, filename, data))
        
        # Return the most recent previous page (highest page number among candidates)
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)  # Sort by page number, descending
            return candidates[0][2]  # Return the data
        
        return None
    
    def _load_existing_classifications(self):
        """Load existing classifications from CSV if it exists."""
        self.existing_data = {}
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
                print(f"Loaded {len(self.existing_data)} existing classifications")
            except Exception as e:
                print(f"Warning: Could not load existing CSV: {e}")
    
    def _setup_gui(self):
        """Setup the GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)  # Left column (image) gets more space
        main_frame.columnconfigure(1, weight=1)  # Right column (controls)
        main_frame.rowconfigure(1, weight=1)     # Image row gets vertical space
        
        # Progress info - spans both columns at the top
        self.progress_label = ttk.Label(main_frame, text="", font=("Arial", 12, "bold"))
        self.progress_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # LEFT SIDE - Image display
        image_frame = ttk.LabelFrame(main_frame, text="Image", padding="10")
        image_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(1, weight=1)
        
        # Filename display in image frame
        self.filename_label = ttk.Label(image_frame, text="", font=("Arial", 10))
        self.filename_label.grid(row=0, column=0, pady=(0, 10))
        
        # Image display
        self.image_label = ttk.Label(image_frame)
        self.image_label.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # RIGHT SIDE - Classification controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        controls_frame.columnconfigure(0, weight=1)
        
        # Classification options frame
        class_frame = ttk.LabelFrame(controls_frame, text="Classification Options", padding="10")
        class_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 20))
        class_frame.columnconfigure(0, weight=1)
        
        # Only Images (0 or 1)
        only_images_section = ttk.Frame(class_frame)
        only_images_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(only_images_section, text="Only Images (0=No, 1=Yes):", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.only_images_var = tk.StringVar(value="0")  # Default to 0
        only_images_frame = ttk.Frame(only_images_section)
        only_images_frame.pack(anchor=tk.W, pady=(5, 0))
        ttk.Radiobutton(only_images_frame, text="0 (No)", variable=self.only_images_var, value="0").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(only_images_frame, text="1 (Yes)", variable=self.only_images_var, value="1").pack(side=tk.LEFT, padx=5)
        
        # Description Quality (0-5) with detailed scale
        desc_section = ttk.Frame(class_frame)
        desc_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(desc_section, text="Description Quality (0-5):", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        # Description scale hint
        desc_hint = ttk.Label(desc_section, text=(
            "5: Every layer is properly described\n"
            "4: Some layers are improperly described\n"
            "3: Some layer descriptions are missing\n"
            "2: Most layer descriptions are missing\n"
            "1: No description is present\n"
            "0: Skip/Not applicable"
        ), font=("Arial", 8), foreground="gray")
        desc_hint.pack(anchor=tk.W, pady=(2, 0))
        
        self.description_var = tk.StringVar(value="0")  # Default to 0
        desc_frame = ttk.Frame(desc_section)
        desc_frame.pack(anchor=tk.W, pady=(5, 0))
        for i in range(6):  # 0-5
            ttk.Radiobutton(desc_frame, text=str(i), variable=self.description_var, value=str(i)).pack(side=tk.LEFT, padx=5)
        
        # Heights Quality (0-5) with detailed scale
        heights_section = ttk.Frame(class_frame)
        heights_section.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(heights_section, text="Heights Quality (0-5):", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        # Heights scale hint
        heights_hint = ttk.Label(heights_section, text=(
            "5: Every height is right\n"
            "4: Some heights are wrong\n"
            "3: Some heights are missing\n"
            "2: Most heights are missing\n"
            "1: No heights are present\n"
            "0: Skip/Not applicable"
        ), font=("Arial", 8), foreground="gray")
        heights_hint.pack(anchor=tk.W, pady=(2, 0))
        
        self.heights_var = tk.StringVar(value="0")  # Default to 0
        heights_frame = ttk.Frame(heights_section)
        heights_frame.pack(anchor=tk.W, pady=(5, 0))
        for i in range(6):  # 0-5
            ttk.Radiobutton(heights_frame, text=str(i), variable=self.heights_var, value=str(i)).pack(side=tk.LEFT, padx=5)
        
        # Rotate flag (0 or 1)
        rotate_section = ttk.Frame(class_frame)
        rotate_section.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(rotate_section, text="Rotate (0=No, 1=Yes):", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        rotate_hint = ttk.Label(rotate_section, text="Press 'R' key to toggle", font=("Arial", 8), foreground="gray")
        rotate_hint.pack(anchor=tk.W, pady=(2, 0))
        
        self.rotate_var = tk.StringVar(value="0")  # Default to 0
        rotate_frame = ttk.Frame(rotate_section)
        rotate_frame.pack(anchor=tk.W, pady=(5, 0))
        ttk.Radiobutton(rotate_frame, text="0 (No)", variable=self.rotate_var, value="0").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(rotate_frame, text="1 (Yes)", variable=self.rotate_var, value="1").pack(side=tk.LEFT, padx=5)
        
        # Navigation buttons in the right panel
        button_frame = ttk.LabelFrame(controls_frame, text="Navigation", padding="10")
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Create a grid for buttons
        ttk.Button(button_frame, text="Previous", command=self._previous_image).grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="Next (Save & Continue)", command=self._next_image).grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="Save Current", command=self._save_current).grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="Skip", command=self._skip_image).grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="Save All & Exit", command=self._save_and_exit).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Configure button frame columns
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Instructions at the bottom of right panel
        instructions = ttk.Label(controls_frame, text=(
            "Keyboard shortcuts:\n"
            "←→ navigate, Space/Enter=next\n"
            "Esc=save&exit, R=toggle rotate\n"
            "0-1 for 'Only Images'\n"
            "Ctrl+0-5 for Description\n"
            "Alt+0-5 for Heights\n"
            "\nDefault values are 0\n"
            "(skip/not applicable)"
        ), font=("Arial", 9), foreground="gray", justify=tk.LEFT)
        instructions.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Keyboard shortcuts
        self.root.bind('<Left>', lambda e: self._previous_image())
        self.root.bind('<Right>', lambda e: self._next_image())
        self.root.bind('<space>', lambda e: self._next_image())
        self.root.bind('<Return>', lambda e: self._next_image())
        self.root.bind('<Escape>', lambda e: self._save_and_exit())
        
        # Keyboard shortcuts for classification
        for i in range(2):
            self.root.bind(str(i), lambda e, val=str(i): self.only_images_var.set(val))
        for i in range(6):  # 0-5 for description
            self.root.bind(f'<Control-{i}>', lambda e, val=str(i): self.description_var.set(val))
            self.root.bind(f'<Alt-{i}>', lambda e, val=str(i): self.heights_var.set(val))
        
        # R key to toggle rotate
        self.root.bind('r', lambda e: self._toggle_rotate())
        self.root.bind('R', lambda e: self._toggle_rotate())
    
    def _load_current_image(self):
        """Load and display the current image."""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        current_file = self.image_files[self.current_index]
        
        # Update progress
        progress_text = f"Image {self.current_index + 1} of {len(self.image_files)}"
        self.progress_label.config(text=progress_text)
        
        # Update filename
        self.filename_label.config(text=current_file.name)
        
        # Load existing classification if available
        if current_file.name in self.existing_data:
            data = self.existing_data[current_file.name]
            self.only_images_var.set(str(data['only_images']))
            self.description_var.set(str(data['description_quality']))
            self.heights_var.set(str(data['heights_quality']))
            self.rotate_var.set(str(data.get('rotate', 0)))
            print(f"Loaded saved classification for {current_file.name}")
        else:
            # Check if there's a previous page from the same document
            previous_data = self._find_previous_same_document(current_file.name)
            if previous_data:
                # Use previous document's classification as defaults
                self.only_images_var.set(str(previous_data['only_images']))
                self.description_var.set(str(previous_data['description_quality']))
                self.heights_var.set(str(previous_data['heights_quality']))
                self.rotate_var.set(str(previous_data.get('rotate', 0)))
                print(f"✓ Inherited values from previous page for document: {self._get_base_filename(current_file.name)}")
                print(f"  Values: Only Images={previous_data['only_images']}, Description={previous_data['description_quality']}, Heights={previous_data['heights_quality']}, Rotate={previous_data.get('rotate', 0)}")
            else:
                # Set default values (0 for all)
                self.only_images_var.set("0")
                self.description_var.set("0")
                self.heights_var.set("0")
                self.rotate_var.set("0")
                print(f"No previous data found for {current_file.name}, using defaults (0,0,0,0)")
        
        try:
            # Load and resize image
            image = Image.open(current_file)
            
            # Calculate size to fit in left panel (max 600x700 for better side-by-side layout)
            max_width, max_height = 600, 700
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update label
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.image_label.config(text=f"Error loading image: {e}")
            print(f"Error loading {current_file}: {e}")
    
    def _get_current_classification(self):
        """Get the current classification values."""
        try:
            only_images = int(self.only_images_var.get()) if self.only_images_var.get() else 0
            description = int(self.description_var.get()) if self.description_var.get() else 0
            heights = int(self.heights_var.get()) if self.heights_var.get() else 0
            rotate = int(self.rotate_var.get()) if self.rotate_var.get() else 0
            return only_images, description, heights, rotate
        except ValueError:
            return 0, 0, 0, 0
    
    def _save_current(self):
        """Save the current classification."""
        if self.current_index >= len(self.image_files):
            return
        
        only_images, description, heights, rotate = self._get_current_classification()
        
        # No validation required - 0 is a valid default value
        current_file = self.image_files[self.current_index]
        classification = {
            'filename': current_file.name,
            'only_images': only_images,
            'description_quality': description,
            'heights_quality': heights,
            'rotate': rotate
        }
        
        # Update existing data
        self.existing_data[current_file.name] = {
            'only_images': only_images,
            'description_quality': description,
            'heights_quality': heights,
            'rotate': rotate
        }
        
        print(f"Saved classification for {current_file.name}: Only Images={only_images}, Description={description}, Heights={heights}, Rotate={rotate}")
        return True
    
    def _next_image(self):
        """Save current and move to next image."""
        if self._save_current():
            if self.current_index < len(self.image_files) - 1:
                self.current_index += 1
                self._load_current_image()
            else:
                messagebox.showinfo("Complete", "You've reached the last image!")
    
    def _previous_image(self):
        """Move to previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            self._load_current_image()
    
    def _skip_image(self):
        """Skip current image without saving."""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self._load_current_image()
        else:
            messagebox.showinfo("Complete", "You've reached the last image!")
    
    def _toggle_rotate(self):
        """Toggle the rotate flag between 0 and 1."""
        current_value = self.rotate_var.get()
        new_value = "1" if current_value == "0" else "0"
        self.rotate_var.set(new_value)
        print(f"Rotate toggled to: {new_value}")
    
    def _save_all_classifications(self):
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
            
            print(f"Saved {len(self.existing_data)} classifications to {self.output_csv}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {e}")
            return False
    
    def _save_and_exit(self):
        """Save all data and exit."""
        if self._save_all_classifications():
            messagebox.showinfo("Saved", f"Classifications saved to {self.output_csv}")
            self.root.quit()
    
    def run(self):
        """Start the GUI application."""
        if not self.image_files:
            return
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._save_and_exit)
        
        print(f"Starting image classifier with {len(self.image_files)} images")
        print("Controls:")
        print("- Use radio buttons or keyboard shortcuts to classify")
        print("- Arrow keys to navigate, Space/Enter to save & continue")
        print("- Esc to save all and exit")
        
        self.root.mainloop()


def main():
    """Main function to run the image classifier."""
    import sys
    
    # Check command line arguments
    image_dir = "data/output/draw"
    output_csv = "image_classifications.csv"
    
    if len(sys.argv) > 1:
        image_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_csv = sys.argv[2]
    
    # Create and run classifier
    classifier = ImageClassifier(image_dir, output_csv)
    classifier.run()


if __name__ == "__main__":
    main()
