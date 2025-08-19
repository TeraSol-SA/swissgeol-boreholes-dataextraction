import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
from pathlib import Path


class LayerEditDialog:
    """Dialog for editing layer information"""
    
    def __init__(self, parent, title, start_depth="", end_depth="", material=""):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create form
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Start depth
        ttk.Label(frame, text="Start Depth:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_var = tk.StringVar(value=start_depth)
        ttk.Entry(frame, textvariable=self.start_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # End depth
        ttk.Label(frame, text="End Depth:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_var = tk.StringVar(value=end_depth)
        ttk.Entry(frame, textvariable=self.end_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Material description
        ttk.Label(frame, text="Material Description:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.material_text = tk.Text(frame, width=40, height=8)
        self.material_text.grid(row=2, column=1, columnspan=2, sticky=tk.EW, pady=5)
        self.material_text.insert("1.0", material)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def ok_clicked(self):
        """Handle OK button click"""
        start = self.start_var.get().strip()
        end = self.end_var.get().strip()
        material = self.material_text.get("1.0", tk.END).strip()
        
        # Validate numeric inputs
        try:
            if start and start != '':
                float(start)
            if end and end != '':
                float(end)
        except ValueError:
            messagebox.showerror("Error", "Depth values must be numeric")
            return
        
        if not material:
            messagebox.showerror("Error", "Material description is required")
            return
        
        self.result = (start, end, material)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()


class GroundwaterEditDialog:
    """Dialog for editing groundwater information"""
    
    def __init__(self, parent, title, date="", depth="", elevation=""):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create form
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Date
        ttk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value=date)
        ttk.Entry(frame, textvariable=self.date_var, width=20).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Depth
        ttk.Label(frame, text="Depth:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.depth_var = tk.StringVar(value=depth)
        ttk.Entry(frame, textvariable=self.depth_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Elevation
        ttk.Label(frame, text="Elevation:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.elevation_var = tk.StringVar(value=elevation)
        ttk.Entry(frame, textvariable=self.elevation_var, width=20).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def ok_clicked(self):
        """Handle OK button click"""
        date = self.date_var.get().strip()
        depth = self.depth_var.get().strip()
        elevation = self.elevation_var.get().strip()
        
        # Validate numeric inputs
        try:
            if depth and depth != '':
                float(depth)
            if elevation and elevation != '':
                float(elevation)
        except ValueError:
            messagebox.showerror("Error", "Depth and elevation must be numeric")
            return
        
        self.result = (date, depth, elevation)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()


class GroundTruthGUI:
    """
    GUI Application to display PNG images and edit their corresponding JSON data
    """

    def __init__(self, input_dir="data/output/draw", output_dir="data/output"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.current_image_index = 0
        self.image_files = []
        self.json_files = []
        self.current_json_data = None
        self.current_pdf_data = None
        self.json_file_path = None
        self.modified = False
        
        # Create main window
        self.window = tk.Tk()
        self.window.title("Ground Truth Dataset Creator")
        self.window.geometry("1600x900")
        
        # Bind keyboard shortcuts
        self.window.bind('<Return>', self.save_on_enter)
        self.window.bind('<KP_Enter>', self.save_on_enter)  # Numeric keypad Enter
        self.window.focus_set()  # Ensure window can receive keyboard events
        
        self.setup_ui()
        self.load_files()

    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File selection buttons
        ttk.Button(control_frame, text="Select Image Directory", 
                  command=self.select_image_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Select JSON File", 
                  command=self.select_json_file).pack(side=tk.LEFT, padx=(0, 5))
        
        # Save button
        self.save_button = ttk.Button(control_frame, text="Save Ground Truth Data", 
                                     command=self.save_current_pdf_data, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=(10, 5))
        
        # Navigation buttons
        ttk.Button(control_frame, text="Next", 
                  command=self.next_image).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(control_frame, text="Previous", 
                  command=self.previous_image).pack(side=tk.RIGHT, padx=(5, 0))
        
        
        # Current file label
        self.file_label = ttk.Label(control_frame, text="No files loaded")
        self.file_label.pack(side=tk.RIGHT, padx=(5, 10))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left frame for image (fills available space)
        left_frame = ttk.LabelFrame(content_frame, text="Image", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Image canvas with scrollbars (fills the frame)
        canvas_frame = ttk.Frame(left_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_canvas = tk.Canvas(canvas_frame, bg="white")
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        self.image_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Bind canvas resize event to redisplay image
        self.image_canvas.bind('<Configure>', self.on_canvas_configure)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right frame for JSON data (fixed width)
        right_frame = ttk.LabelFrame(content_frame, text="Ground Truth Data", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=(5, 0))
        right_frame.configure(width=500)  # Fixed width so left side gets remaining space
        
        # Notebook for different data sections
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Layers tab
        self.layers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.layers_frame, text="Layers")
        
        # Layers controls
        layers_control_frame = ttk.Frame(self.layers_frame)
        layers_control_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(layers_control_frame, text="Add Layer", 
                  command=self.add_layer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(layers_control_frame, text="Delete Selected", 
                  command=self.delete_layer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(layers_control_frame, text="Edit Selected", 
                  command=self.edit_layer).pack(side=tk.LEFT, padx=(0, 5))
        
        # Add move buttons
        ttk.Button(layers_control_frame, text="Move Up ↑", 
                  command=self.move_layer_up).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Button(layers_control_frame, text="Move Down ↓", 
                  command=self.move_layer_down).pack(side=tk.LEFT, padx=(2, 5))
        
        # Layers treeview
        layers_tree_frame = ttk.Frame(self.layers_frame)
        layers_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.layers_tree = ttk.Treeview(layers_tree_frame, columns=("depth_start", "depth_end", "material", "ref"), show="headings")
        self.layers_tree.heading("depth_start", text="Start Depth")
        self.layers_tree.heading("depth_end", text="End Depth")
        self.layers_tree.heading("material", text="Material Description")
        self.layers_tree.column("depth_start", width=80)
        self.layers_tree.column("depth_end", width=80)
        self.layers_tree.column("material", width=400)
        self.layers_tree.column("ref", width=0, stretch=False)  # Hidden column for reference
        self.layers_tree.heading("ref", text="")
        
        layers_scrollbar = ttk.Scrollbar(layers_tree_frame, orient=tk.VERTICAL, command=self.layers_tree.yview)
        self.layers_tree.configure(yscrollcommand=layers_scrollbar.set)
        
        self.layers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        layers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Groundwater tab
        self.groundwater_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.groundwater_frame, text="Groundwater")
        
        # Groundwater controls
        gw_control_frame = ttk.Frame(self.groundwater_frame)
        gw_control_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(gw_control_frame, text="Add Groundwater", 
                  command=self.add_groundwater).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(gw_control_frame, text="Delete Selected", 
                  command=self.delete_groundwater).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(gw_control_frame, text="Edit Selected", 
                  command=self.edit_groundwater).pack(side=tk.LEFT, padx=(0, 5))
        
        # Groundwater treeview
        gw_tree_frame = ttk.Frame(self.groundwater_frame)
        gw_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.groundwater_tree = ttk.Treeview(gw_tree_frame, columns=("date", "depth", "elevation", "ref"), show="headings")
        self.groundwater_tree.heading("date", text="Date")
        self.groundwater_tree.heading("depth", text="Depth")
        self.groundwater_tree.heading("elevation", text="Elevation")
        self.groundwater_tree.column("date", width=100)
        self.groundwater_tree.column("depth", width=80)
        self.groundwater_tree.column("elevation", width=80)
        self.groundwater_tree.column("ref", width=0, stretch=False)  # Hidden column for reference
        self.groundwater_tree.heading("ref", text="")
        
        groundwater_scrollbar = ttk.Scrollbar(gw_tree_frame, orient=tk.VERTICAL, command=self.groundwater_tree.yview)
        self.groundwater_tree.configure(yscrollcommand=groundwater_scrollbar.set)
        
        self.groundwater_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        groundwater_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Metadata tab
        self.metadata_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.metadata_frame, text="Metadata")
        
        # Metadata text widget
        self.metadata_text = tk.Text(self.metadata_frame, wrap=tk.WORD, width=50, height=20)
        metadata_scrollbar = ttk.Scrollbar(self.metadata_frame, orient=tk.VERTICAL, command=self.metadata_text.yview)
        self.metadata_text.configure(yscrollcommand=metadata_scrollbar.set)
        
        self.metadata_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        metadata_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def select_image_directory(self):
        """Select directory containing PNG images"""
        directory = filedialog.askdirectory(title="Select Image Directory")
        if directory:
            self.input_dir = Path(directory)
            self.load_image_files()
            self.update_display()

    def select_json_file(self):
        """Select JSON file containing the data"""
        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.load_json_file(file_path)
            self.update_display()

    def load_files(self):
        """Load initial files from default directories"""
        self.load_image_files()
        # Try to load predictions JSON from output directory (default behavior)
        predictions_json = self.output_dir / "predictions.json"
        if predictions_json.exists():
            self.load_json_file(str(predictions_json))
        else:
            # Fallback to filtered predictions
            predictions_json = self.output_dir / "predictions_filtered.json" 
            if predictions_json.exists():
                self.load_json_file(str(predictions_json))

    def load_image_files(self):
        """Load all PNG files from the input directory"""
        self.image_files = []
        if self.input_dir.exists():
            for ext in ['*.png', '*.PNG']:
                self.image_files.extend(self.input_dir.glob(ext))
        self.image_files.sort()
        self.current_image_index = 0

    def load_json_file(self, file_path):
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                self.current_json_data = json.load(f)
            self.json_file_path = file_path
            self.status_label.config(text=f"Loaded: {Path(file_path).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file: {str(e)}")
            self.current_json_data = None
            self.json_file_path = None

    def get_current_pdf_name(self):
        """Get the PDF name corresponding to current image"""
        if not self.image_files or self.current_image_index >= len(self.image_files):
            return None
        
        current_image = self.image_files[self.current_image_index]
        # Convert PNG name from format like "filename.pdf_page1.png" to "filename.pdf"
        image_name = current_image.stem  # e.g., "filename.pdf_page1"
        
        # Extract PDF name by removing the "_pageN" suffix
        if "_page" in image_name:
            pdf_name = image_name.split("_page")[0]
            # Ensure it ends with .pdf
            if not pdf_name.endswith('.pdf'):
                pdf_name += '.pdf'
        else:
            # Fallback: assume the image name directly corresponds to PDF
            pdf_name = image_name + ".pdf"
        
        return pdf_name

    def get_current_pdf_data(self):
        """Get the PDF data for current image"""
        if not self.current_json_data:
            return None
        
        pdf_name = self.get_current_pdf_name()
        if not pdf_name:
            return None
        
        return self.current_json_data.get(pdf_name, None)

    def set_modified(self, modified=True):
        """Set the modified flag and update UI"""
        self.modified = modified
        if modified:
            self.status_label.config(text="Ground truth modified - unsaved changes")
            self.save_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Auto-extracted data loaded - review and correct as needed")
            self.save_button.config(state=tk.DISABLED)

    def display_image(self):
        """Display the current image, scaling it to fit the available canvas space"""
        if not self.image_files or self.current_image_index >= len(self.image_files):
            self.image_canvas.delete("all")
            return
        
        image_path = self.image_files[self.current_image_index]
        try:
            # Load image
            image = Image.open(image_path)
            
            # Get canvas dimensions
            self.image_canvas.update_idletasks()  # Ensure canvas is rendered
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            # Skip if canvas is not yet rendered properly
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 800  # Fallback width
                canvas_height = 600  # Fallback height
            
            # Calculate scaling to fit the canvas while maintaining aspect ratio
            image_width, image_height = image.size
            scale_x = canvas_width / image_width
            scale_y = canvas_height / image_height
            scale = min(scale_x, scale_y)  # Use the smaller scale to fit both dimensions
            
            # Only scale down if image is larger than canvas, or scale up if much smaller
            if scale < 1.0 or (scale > 2.0 and image_width < canvas_width // 2):
                new_width = int(image_width * scale)
                new_height = int(image_height * scale)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(image)
            self.image_canvas.delete("all")
            
            # Center the image in the canvas
            img_width, img_height = image.size
            x = max(0, (canvas_width - img_width) // 2)
            y = max(0, (canvas_height - img_height) // 2)
            
            self.image_canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
            self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def display_json_data(self):
        """Display JSON data in the right panel"""
        # Clear existing data
        for item in self.layers_tree.get_children():
            self.layers_tree.delete(item)
        for item in self.groundwater_tree.get_children():
            self.groundwater_tree.delete(item)
        self.metadata_text.delete(1.0, tk.END)
        
        self.current_pdf_data = self.get_current_pdf_data()
        if not self.current_pdf_data:
            # Show message when no automatic data is found
            self.metadata_text.insert(tk.END, "No auto-extracted data found for this image.\n")
            self.metadata_text.insert(tk.END, "You can manually add layers and groundwater data using the buttons above.\n")
            self.status_label.config(text="No auto-extracted data - manual entry required")
            return
        
        # Show status that auto-extracted data was loaded
        self.status_label.config(text="Auto-extracted data loaded - review and correct as needed")
        
        # Display data for all boreholes in the current PDF
        boreholes = self.current_pdf_data.get('boreholes', [])
        
        for i, borehole in enumerate(boreholes):
            borehole_prefix = f"BH{borehole.get('borehole_index', i)}: "
            
            # Display layers
            layers = borehole.get('layers', [])
            for j, layer in enumerate(layers):
                # Get material description
                material_desc = layer.get('material_description', {})
                if isinstance(material_desc, dict):
                    material_text = material_desc.get('text', 'N/A')
                else:
                    material_text = str(material_desc) if material_desc else 'N/A'
                
                # Get depths
                depths = layer.get('depths', {})
                start_depth = 'N/A'
                end_depth = 'N/A'
                
                if depths:
                    start_info = depths.get('start')
                    end_info = depths.get('end')
                    
                    if start_info and isinstance(start_info, dict):
                        start_depth = start_info.get('value', 'N/A')
                    elif start_info is not None:
                        start_depth = start_info
                        
                    if end_info and isinstance(end_info, dict):
                        end_depth = end_info.get('value', 'N/A')
                    elif end_info is not None:
                        end_depth = end_info
                
                # Insert into tree with item ID for later reference
                item_id = self.layers_tree.insert("", tk.END, values=(
                    str(start_depth),
                    str(end_depth),
                    f"{borehole_prefix}{material_text}",
                    f"{i}_{j}"  # Reference for borehole_layer index
                ))
            
            # Display groundwater
            groundwater = borehole.get('groundwater', [])
            for j, gw in enumerate(groundwater):
                date = gw.get('date', 'N/A')
                depth = gw.get('depth', 'N/A')
                elevation = gw.get('elevation', 'N/A')
                
                item_id = self.groundwater_tree.insert("", tk.END, values=(
                    str(date),
                    str(depth),
                    str(elevation),
                    f"{i}_{j}"  # Reference for borehole_gw index
                ))
            
            # Display metadata
            metadata = borehole.get('metadata', {})
            metadata_text = f"=== Auto-extracted Borehole {borehole.get('borehole_index', i)} ===\n"
            metadata_text += "Review the data below and make corrections as needed.\n\n"
            
            elevation = metadata.get('elevation', 'N/A')
            metadata_text += f"Elevation: {elevation}\n"
            
            coordinates = metadata.get('coordinates', {})
            if coordinates:
                e_coord = coordinates.get('E', 'N/A')
                n_coord = coordinates.get('N', 'N/A')
                metadata_text += f"Coordinates: E={e_coord}, N={n_coord}\n"
            
            metadata_text += f"\nLayers found: {len(layers)}\n"
            metadata_text += f"Groundwater entries: {len(groundwater)}\n"
            metadata_text += "\n"
            self.metadata_text.insert(tk.END, metadata_text)

    def update_display(self):
        """Update both image and JSON display"""
        if self.image_files:
            current_file = self.image_files[self.current_image_index].name
            self.file_label.config(text=f"File {self.current_image_index + 1}/{len(self.image_files)}: {current_file}")
        else:
            self.file_label.config(text="No files loaded")
        
        self.display_image()
        self.display_json_data()

    def next_image(self):
        """Navigate to next image"""
        if self.image_files and self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.update_display()

    def previous_image(self):
        """Navigate to previous image"""
        if self.image_files and self.current_image_index > 0:
            self.current_image_index -= 1
            self.update_display()

    # Editing functionality
    def add_layer(self):
        """Add a new layer"""
        if not self.current_pdf_data:
            messagebox.showwarning("Warning", "No PDF data loaded")
            return
        
        dialog = LayerEditDialog(self.window, "Add Layer")
        if dialog.result:
            start_depth, end_depth, material = dialog.result
            
            # Add to first borehole (or create one if none exist)
            boreholes = self.current_pdf_data.setdefault('boreholes', [])
            if not boreholes:
                boreholes.append({
                    'borehole_index': 0,
                    'metadata': {'elevation': None, 'coordinates': {}},
                    'layers': [],
                    'groundwater': []
                })
            
            # Create new layer
            new_layer = {
                'material_description': {'text': material},
                'depths': {
                    'start': {'value': start_depth} if start_depth != '' else None,
                    'end': {'value': end_depth} if end_depth != '' else None
                }
            }
            
            boreholes[0]['layers'].append(new_layer)
            self.set_modified(True)
            self.display_json_data()

    def delete_layer(self):
        """Delete selected layer"""
        selection = self.layers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a layer to delete")
            return
        
        if messagebox.askyesno("Confirm", "Delete selected layer?"):
            for item_id in selection:
                # Get the borehole and layer indices
                values = self.layers_tree.item(item_id, 'values')
                if len(values) >= 4:
                    ref = values[3]  # Reference is in 4th column
                    if ref:
                        borehole_idx, layer_idx = map(int, ref.split('_'))
                        
                        # Remove from data
                        boreholes = self.current_pdf_data.get('boreholes', [])
                        if borehole_idx < len(boreholes):
                            layers = boreholes[borehole_idx].get('layers', [])
                            if layer_idx < len(layers):
                                layers.pop(layer_idx)
                                self.set_modified(True)
            
            self.display_json_data()

    def edit_layer(self):
        """Edit selected layer"""
        selection = self.layers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a layer to edit")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one layer to edit")
            return
        
        item_id = selection[0]
        values = self.layers_tree.item(item_id, 'values')
        if len(values) < 4:
            return
        
        ref = values[3]  # Reference is in 4th column
        if not ref:
            return
        
        borehole_idx, layer_idx = map(int, ref.split('_'))
        boreholes = self.current_pdf_data.get('boreholes', [])
        
        if borehole_idx >= len(boreholes):
            return
        
        layers = boreholes[borehole_idx].get('layers', [])
        if layer_idx >= len(layers):
            return
        
        layer = layers[layer_idx]
        
        # Get current values
        material_desc = layer.get('material_description', {})
        current_material = material_desc.get('text', '') if isinstance(material_desc, dict) else str(material_desc)
        
        depths = layer.get('depths', {})
        current_start = ''
        current_end = ''
        
        if depths:
            start_info = depths.get('start')
            end_info = depths.get('end')
            
            if start_info and isinstance(start_info, dict):
                current_start = str(start_info.get('value', ''))
            elif start_info is not None:
                current_start = str(start_info)
                
            if end_info and isinstance(end_info, dict):
                current_end = str(end_info.get('value', ''))
            elif end_info is not None:
                current_end = str(end_info)
        
        # Show edit dialog
        dialog = LayerEditDialog(self.window, "Edit Layer", current_start, current_end, current_material)
        if dialog.result:
            start_depth, end_depth, material = dialog.result
            
            # Update layer
            layer['material_description'] = {'text': material}
            layer['depths'] = {
                'start': {'value': float(start_depth)} if start_depth != '' else None,
                'end': {'value': float(end_depth)} if end_depth != '' else None
            }
            
            self.set_modified(True)
            self.display_json_data()

    def add_groundwater(self):
        """Add new groundwater entry"""
        if not self.current_pdf_data:
            messagebox.showwarning("Warning", "No PDF data loaded")
            return
        
        dialog = GroundwaterEditDialog(self.window, "Add Groundwater")
        if dialog.result:
            date, depth, elevation = dialog.result
            
            # Add to first borehole
            boreholes = self.current_pdf_data.setdefault('boreholes', [])
            if not boreholes:
                boreholes.append({
                    'borehole_index': 0,
                    'metadata': {'elevation': None, 'coordinates': {}},
                    'layers': [],
                    'groundwater': []
                })
            
            new_gw = {
                'date': date,
                'depth': float(depth) if depth != '' else None,
                'elevation': float(elevation) if elevation != '' else None
            }
            
            boreholes[0]['groundwater'].append(new_gw)
            self.set_modified(True)
            self.display_json_data()

    def delete_groundwater(self):
        """Delete selected groundwater entry"""
        selection = self.groundwater_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a groundwater entry to delete")
            return
        
        if messagebox.askyesno("Confirm", "Delete selected groundwater entry?"):
            for item_id in selection:
                values = self.groundwater_tree.item(item_id, 'values')
                if len(values) >= 4:
                    ref = values[3]  # Reference is in 4th column
                    if ref:
                        borehole_idx, gw_idx = map(int, ref.split('_'))
                        
                        boreholes = self.current_pdf_data.get('boreholes', [])
                        if borehole_idx < len(boreholes):
                            groundwater = boreholes[borehole_idx].get('groundwater', [])
                            if gw_idx < len(groundwater):
                                groundwater.pop(gw_idx)
                                self.set_modified(True)
            
            self.display_json_data()

    def edit_groundwater(self):
        """Edit selected groundwater entry"""
        selection = self.groundwater_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a groundwater entry to edit")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one groundwater entry to edit")
            return
        
        item_id = selection[0]
        values = self.groundwater_tree.item(item_id, 'values')
        if len(values) < 4:
            return
        
        ref = values[3]  # Reference is in 4th column
        if not ref:
            return
        
        borehole_idx, gw_idx = map(int, ref.split('_'))
        boreholes = self.current_pdf_data.get('boreholes', [])
        
        if borehole_idx >= len(boreholes):
            return
        
        groundwater = boreholes[borehole_idx].get('groundwater', [])
        if gw_idx >= len(groundwater):
            return
        
        gw = groundwater[gw_idx]
        
        # Get current values
        current_date = str(gw.get('date', ''))
        current_depth = str(gw.get('depth', ''))
        current_elevation = str(gw.get('elevation', ''))
        
        # Show edit dialog
        dialog = GroundwaterEditDialog(self.window, "Edit Groundwater", current_date, current_depth, current_elevation)
        if dialog.result:
            date, depth, elevation = dialog.result
            
            # Update groundwater entry
            gw['date'] = date
            gw['depth'] = float(depth) if depth != '' else None
            gw['elevation'] = float(elevation) if elevation != '' else None
            
            self.set_modified(True)
            self.display_json_data()

    def move_layer_up(self):
        """Move selected layer up in the list"""
        selection = self.layers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a layer to move")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one layer to move")
            return
        
        item_id = selection[0]
        values = self.layers_tree.item(item_id, 'values')
        if len(values) < 4:
            return
        
        ref = values[3]  # Reference is in 4th column
        if not ref:
            return
        
        borehole_idx, layer_idx = map(int, ref.split('_'))
        boreholes = self.current_pdf_data.get('boreholes', [])
        
        if borehole_idx >= len(boreholes):
            return
        
        layers = boreholes[borehole_idx].get('layers', [])
        if layer_idx >= len(layers) or layer_idx <= 0:
            return  # Can't move up if it's already at the top
        
        # Swap with the layer above
        layers[layer_idx], layers[layer_idx - 1] = layers[layer_idx - 1], layers[layer_idx]
        
        self.set_modified(True)
        self.display_json_data()
        
        # Re-select the moved layer (now at layer_idx - 1)
        self._select_layer_by_index(borehole_idx, layer_idx - 1)

    def move_layer_down(self):
        """Move selected layer down in the list"""
        selection = self.layers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a layer to move")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one layer to move")
            return
        
        item_id = selection[0]
        values = self.layers_tree.item(item_id, 'values')
        if len(values) < 4:
            return
        
        ref = values[3]  # Reference is in 4th column
        if not ref:
            return
        
        borehole_idx, layer_idx = map(int, ref.split('_'))
        boreholes = self.current_pdf_data.get('boreholes', [])
        
        if borehole_idx >= len(boreholes):
            return
        
        layers = boreholes[borehole_idx].get('layers', [])
        if layer_idx >= len(layers) - 1:
            return  # Can't move down if it's already at the bottom
        
        # Swap with the layer below
        layers[layer_idx], layers[layer_idx + 1] = layers[layer_idx + 1], layers[layer_idx]
        
        self.set_modified(True)
        self.display_json_data()
        
        # Re-select the moved layer (now at layer_idx + 1)
        self._select_layer_by_index(borehole_idx, layer_idx + 1)

    def _select_layer_by_index(self, borehole_idx, layer_idx):
        """Helper method to select a layer by its borehole and layer index"""
        for item_id in self.layers_tree.get_children():
            values = self.layers_tree.item(item_id, 'values')
            if len(values) >= 4:
                ref = values[3]
                if ref == f"{borehole_idx}_{layer_idx}":
                    self.layers_tree.selection_set(item_id)
                    self.layers_tree.focus(item_id)
                    break

    def save_current_pdf_data(self, show_popup=True):
        """Save current PDF data as ground truth to a new JSON file"""
        if not self.current_pdf_data and not self.has_manual_data():
            if show_popup:
                messagebox.showwarning("Warning", "No data to save")
            return
        
        pdf_name = self.get_current_pdf_name()
        if not pdf_name:
            if show_popup:
                messagebox.showwarning("Warning", "No current PDF identified")
            return
        
        # Create output filename for ground truth
        output_filename = pdf_name.replace('.pdf', '_ground_truth.json')
        output_path = self.output_dir / "ground_truth" / output_filename
        
        # Ensure ground_truth directory exists
        output_path.parent.mkdir(exist_ok=True)
        
        # Create simplified ground truth data structure
        ground_truth_data = {pdf_name: self.extract_simplified_data()}
        
        try:
            with open(output_path, 'w') as f:
                json.dump(ground_truth_data, f, indent=2)
            
            if show_popup:
                messagebox.showinfo("Success", f"Ground truth saved to ground_truth/{output_filename}")
            else:
                # Update status without popup - show briefly then clear
                self.status_label.config(text=f"✓ Saved: {output_filename}")
                self.window.after(2000, lambda: self.status_label.config(text="Auto-extracted data loaded - review and correct as needed") if not self.modified else None)
            
            self.set_modified(False)
            
        except Exception as e:
            if show_popup:
                messagebox.showerror("Error", f"Failed to save ground truth: {str(e)}")
            else:
                self.status_label.config(text=f"Error saving: {str(e)}")

    def has_manual_data(self):
        """Check if there's any manual data entered when no auto-extracted data exists"""
        return (len(self.layers_tree.get_children()) > 0 or 
                len(self.groundwater_tree.get_children()) > 0)

    def extract_simplified_data(self):
        """Extract only the requested fields from current PDF data"""
        if not self.current_pdf_data:
            return []
        
        simplified_boreholes = []
        boreholes = self.current_pdf_data.get('boreholes', [])
        
        for borehole in boreholes:
            simplified_borehole = {
                'borehole_index': borehole.get('borehole_index', 0),
                'layers': [],
                'groundwater': [],
                'metadata': {}
            }
            
            # Extract layers with only material_description and depth_interval
            for layer in borehole.get('layers', []):
                material_desc = layer.get('material_description', {})
                material_text = material_desc.get('text', '') if isinstance(material_desc, dict) else str(material_desc)
                
                depths = layer.get('depths', {})
                depth_interval = {}
                
                if depths:
                    start_info = depths.get('start')
                    end_info = depths.get('end')
                    
                    if start_info and isinstance(start_info, dict):
                        depth_interval['start'] = start_info.get('value')
                    elif start_info is not None:
                        depth_interval['start'] = start_info
                    
                    if end_info and isinstance(end_info, dict):
                        depth_interval['end'] = end_info.get('value')
                    elif end_info is not None:
                        depth_interval['end'] = end_info
                
                simplified_layer = {
                    'material_description': material_text,
                    'depth_interval': depth_interval
                }
                simplified_borehole['layers'].append(simplified_layer)
            
            # Extract groundwater with depth and elevation
            for gw in borehole.get('groundwater', []):
                simplified_gw = {
                    'date': gw.get('date'),
                    'depth': gw.get('depth'),
                    'elevation': gw.get('elevation')
                }
                simplified_borehole['groundwater'].append(simplified_gw)
            
            # Extract elevation from metadata
            metadata = borehole.get('metadata', {})
            if metadata.get('elevation'):
                simplified_borehole['metadata']['elevation'] = metadata['elevation']
            
            coordinates = metadata.get('coordinates', {})
            if coordinates and ('E' in coordinates or 'N' in coordinates):
                simplified_borehole['metadata']['coordinates'] = {
                    'E': coordinates.get('E'),
                    'N': coordinates.get('N')
                }
            
            simplified_boreholes.append(simplified_borehole)
        
        return simplified_boreholes

    def on_canvas_configure(self, event):
        """Handle canvas resize event to redisplay image"""
        # Only redisplay if the canvas size actually changed significantly
        if hasattr(self, '_last_canvas_size'):
            last_width, last_height = self._last_canvas_size
            if abs(event.width - last_width) < 10 and abs(event.height - last_height) < 10:
                return  # Skip minor resize events
        
        self._last_canvas_size = (event.width, event.height)
        
        # Redisplay the current image to fit the new canvas size
        if hasattr(self, 'image_files') and self.image_files:
            self.window.after_idle(self.display_image)  # Schedule redisplay to avoid recursion

    def save_on_enter(self, event):
        """Handle Enter key press to save current file and move to next"""
        # Only save if there's data to save or if save button is enabled
        if self.current_pdf_data or self.has_manual_data():
            # Save without showing popup
            self.save_current_pdf_data(show_popup=False)
            # Move to next image
            self.next_image()
        else:
            # If no data to save, just move to next image
            self.next_image()
        return "break"  # Prevent event from propagating

    def main(self):
        """Start the GUI application"""
        self.update_display()
        self.window.mainloop()


if __name__ == "__main__":
    app = GroundTruthGUI()
    app.main()