import tkinter as tk
from tkinter import messagebox, filedialog, Menu, simpledialog, ttk
from PIL import Image, ImageTk
import sys
from pathlib import Path
from config_manager import ConfigManager
from file_handler import FileHandler


class ImageSorter:
    def __init__(self, folder_path=None):
        self.root = tk.Tk()
        self.root.title("Image Sorter")
        
        self.config_manager = ConfigManager()
        window_config = self.config_manager.get_window_config()
        
        if window_config.get("fullscreen", False):
            self.root.attributes('-fullscreen', True)
        else:
            width = window_config.get("width", 1200)
            height = window_config.get("height", 800)
            self.root.geometry(f"{width}x{height}")
            self.root.minsize(800, 600)
        
        self.root.configure(bg=window_config.get("background_color", "#000000"))
        
        self.folder_path = None
        self.file_handler = None
        self.image_files = []
        self.current_index = 0
        
        self.setup_ui()
        self.bind_keys()
        
        # Bind window resize event
        self.root.bind('<Configure>', self.on_window_resize)
        
        if folder_path:
            self.load_folder(Path(folder_path))
        else:
            self.show_no_folder_message()
    
    def _select_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing images")
        return Path(folder) if folder else None
    
    def setup_ui(self):
        self.create_menu()
        
        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=0)  # Top action label
        self.root.grid_rowconfigure(1, weight=1)  # Main content row
        self.root.grid_rowconfigure(2, weight=0)  # Bottom info/action
        self.root.grid_columnconfigure(0, weight=0)  # Left action
        self.root.grid_columnconfigure(1, weight=1)  # Center content
        self.root.grid_columnconfigure(2, weight=0)  # Right action
        
        # Create grid areas
        self.top_frame = tk.Frame(self.root, bg=self.root.cget('bg'))
        self.top_frame.grid(row=0, column=1, pady=5, sticky="ew")
        
        self.left_frame = tk.Frame(self.root, bg=self.root.cget('bg'), width=120)
        self.left_frame.grid(row=1, column=0, padx=5, sticky="ns")
        self.left_frame.grid_propagate(False)
        
        self.center_frame = tk.Frame(self.root, bg=self.root.cget('bg'))
        self.center_frame.grid(row=1, column=1, sticky="nsew")
        
        self.right_frame = tk.Frame(self.root, bg=self.root.cget('bg'), width=120)
        self.right_frame.grid(row=1, column=2, padx=5, sticky="ns")
        self.right_frame.grid_propagate(False)
        
        self.bottom_frame = tk.Frame(self.root, bg=self.root.cget('bg'))
        self.bottom_frame.grid(row=2, column=1, pady=5, sticky="ew")
        
        # Image in center
        self.image_label = tk.Label(self.center_frame, bg=self.root.cget('bg'))
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Info labels in bottom
        self.progress_label = tk.Label(
            self.bottom_frame, 
            text="", 
            fg="white", 
            bg=self.root.cget('bg'),
            font=("Arial", 12)
        )
        self.progress_label.pack()
        
        self.status_label = tk.Label(
            self.bottom_frame, 
            text="Use File > Open Folder to select images", 
            fg="yellow", 
            bg=self.root.cget('bg'),
            font=("Arial", 10)
        )
        self.status_label.pack()
        
        self.action_labels = {}
    
    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Folder...", command=self.open_folder_dialog)
        file_menu.add_separator()
        
        self.search_subfolders_var = tk.BooleanVar(value=self.config_manager.get_search_subfolders())
        file_menu.add_checkbutton(
            label="Search Subfolders", 
            variable=self.search_subfolders_var,
            command=self.toggle_search_subfolders
        )
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find Duplicates...", command=self.find_duplicates_dialog)
    
    def open_folder_dialog(self):
        folder = filedialog.askdirectory(title="Select folder containing images")
        if folder:
            self.load_folder(Path(folder))
    
    def toggle_search_subfolders(self):
        self.config_manager.set_search_subfolders(self.search_subfolders_var.get())
        if self.folder_path:
            self.load_folder(self.folder_path)
    
    def load_folder(self, folder_path):
        self.folder_path = folder_path
        search_subfolders = self.config_manager.get_search_subfolders()
        self.file_handler = FileHandler(self.folder_path, search_subfolders)
        self.image_files = self.file_handler.get_image_files()
        
        if not self.image_files:
            self.show_no_images_message()
            return
        
        self.current_index = 0
        self.create_action_labels()
        self.load_current_image()
        self.status_label.config(text="Use arrow keys to sort images", fg="yellow")
    
    def show_no_folder_message(self):
        self.image_label.configure(text="No folder selected\n\nUse File > Open Folder to select a folder containing images", 
                                 fg="white", font=("Arial", 16), compound="center")
        self.progress_label.config(text="")
    
    def show_no_images_message(self):
        self.image_label.configure(text="No images found in selected folder\n\nTry selecting a different folder or enable 'Search Subfolders'", 
                                 fg="white", font=("Arial", 16), compound="center")
        self.progress_label.config(text="")
    
    def create_action_labels(self):
        for label in self.action_labels.values():
            label.destroy()
        
        self.action_labels = {}
        
        # Create action labels in their respective frames
        action_config = {
            "up": (self.top_frame, "↑"),
            "down": (self.bottom_frame, "↓"), 
            "left": (self.left_frame, "←"),
            "right": (self.right_frame, "→")
        }
        
        for direction, (parent_frame, arrow) in action_config.items():
            action = self.config_manager.get_action(direction)
            text = f"{arrow} {action['name']}"
            
            label = tk.Label(
                parent_frame,
                text=text,
                fg="white",
                bg="black",
                font=("Arial", 14, "bold"),
                padx=10,
                pady=5,
                cursor="hand2"
            )
            
            if direction in ["up", "down"]:
                label.pack(pady=5)
            else:  # left, right
                label.pack(expand=True, anchor="center")
            
            label.bind("<Double-Button-1>", lambda e, d=direction: self.edit_action_name(d))
            self.action_labels[direction] = label
    
    def edit_action_name(self, direction):
        current_action = self.config_manager.get_action(direction)
        current_name = current_action['name']
        
        arrow_symbol = {"up": "↑", "down": "↓", "left": "←", "right": "→"}[direction]
        
        new_name = simpledialog.askstring(
            "Edit Action", 
            f"Enter name for {arrow_symbol} ({direction}) action:\n\n"
            f"Current: {current_name}\n\n"
            f"Tip: Use 'delete' to send files to recycle bin",
            initialvalue=current_name
        )
        
        if new_name is not None and new_name.strip():
            new_name = new_name.strip()
            self.config_manager.set_action_name(direction, new_name)
            self.create_action_labels()
            self.status_label.config(
                text=f"Updated {arrow_symbol} action to: {new_name}", 
                fg="green"
            )
    
    def bind_keys(self):
        self.root.bind('<Key>', self.handle_keypress)
        self.root.focus_set()
    
    def on_window_resize(self, event):
        # Only respond to root window resize events, not child widgets
        if event.widget == self.root and hasattr(self, 'image_files') and self.image_files and hasattr(self, 'current_index'):
            # Delay to let the layout settle
            self.root.after(50, self.reload_current_image)
    
    def reload_current_image(self):
        if hasattr(self, 'image_files') and self.image_files and self.current_index < len(self.image_files):
            self.load_current_image()
    
    def handle_keypress(self, event):
        if not self.image_files:
            return
            
        key_map = {
            'Up': 'up',
            'Down': 'down', 
            'Left': 'left',
            'Right': 'right'
        }
        
        if event.keysym in key_map:
            direction = key_map[event.keysym]
            self.process_image_action(direction)
        elif event.keysym == 'Escape':
            self.root.quit()
        elif event.keysym == 'space':
            self.next_image()
        elif event.keysym == 'BackSpace':
            self.previous_image()
    
    def process_image_action(self, direction):
        if not self.image_files or self.current_index >= len(self.image_files):
            return
            
        current_file = self.image_files[self.current_index]
        action = self.config_manager.get_action(direction)
        
        success, message = self.file_handler.process_action(current_file, action)
        
        if success:
            self.image_files.pop(self.current_index)
            self.status_label.config(text=message, fg="green")
            
            if self.current_index >= len(self.image_files):
                if self.image_files:
                    self.current_index = len(self.image_files) - 1
                else:
                    self.show_completion_message()
                    return
            
            self.load_current_image()
        else:
            self.status_label.config(text=message, fg="red")
    
    def next_image(self):
        if self.image_files and self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_current_image()
    
    def previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()
    
    def load_current_image(self):
        if not self.image_files:
            self.show_completion_message()
            return
            
        current_file = self.image_files[self.current_index]
        self.update_progress()
        
        try:
            image = Image.open(current_file)
            
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            if window_width <= 1 or window_height <= 1:
                self.root.after(100, self.load_current_image)
                return
            
            # Get actual available space from center frame
            self.root.update_idletasks()
            self.center_frame.update_idletasks()
            available_width = self.center_frame.winfo_width()
            available_height = self.center_frame.winfo_height()
            
            # Add some padding to prevent edge touching
            available_width = max(1, available_width - 20)
            available_height = max(1, available_height - 20)
            
            if available_width <= 1 or available_height <= 1:
                self.root.after(100, self.load_current_image)
                return
            
            image_width, image_height = image.size
            scale_factor = min(available_width / image_width, available_height / image_height)
            
            new_width = int(image_width * scale_factor)
            new_height = int(image_height * scale_factor)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=self.photo, text="", compound="center")
            
        except Exception as e:
            self.status_label.config(text=f"Error loading image: {e}", fg="red")
    
    def update_progress(self):
        if self.image_files:
            current = self.current_index + 1
            total = len(self.image_files)
            filename = self.image_files[self.current_index].name
            self.progress_label.config(text=f"{current}/{total} - {filename}")
        else:
            self.progress_label.config(text="No images remaining")
    
    def show_completion_message(self):
        self.image_label.configure(image="")
        self.image_label.configure(text="🎉 Congratulations! 🎉\n\nYou have successfully processed all images!\n\nThere are no more images to sort at this time.\n\nUse File > Open Folder to select a new folder\nor press Escape to exit.", 
                                 fg="green", font=("Arial", 18, "bold"), compound="center")
        self.progress_label.config(text="All images processed successfully!")
        self.status_label.config(text="Use File > Open Folder to load more images or press Escape to exit", fg="white")
        
        for label in self.action_labels.values():
            label.pack_forget()
        
        # Add cleanup button if we used subfolders
        if self.file_handler and self.file_handler.search_subfolders:
            self.cleanup_button = tk.Button(
                self.bottom_frame,
                text="🗑️ Clean Up Empty Subfolders",
                command=self.cleanup_empty_folders,
                bg="#ff6b6b",
                fg="white",
                font=("Arial", 12, "bold"),
                padx=20,
                pady=10,
                cursor="hand2"
            )
            self.cleanup_button.pack(pady=10)
    
    def cleanup_empty_folders(self):
        """Clean up empty subfolders and update the UI"""
        if not self.file_handler:
            return
            
        success, message = self.file_handler.remove_empty_subfolders()
        
        if success:
            self.status_label.config(text=message, fg="green")
            # Hide the cleanup button after use
            if hasattr(self, 'cleanup_button'):
                self.cleanup_button.pack_forget()
        else:
            self.status_label.config(text=message, fg="red")
    
    def find_duplicates_dialog(self):
        """Open dialog to find and manage duplicate files"""
        if not self.file_handler:
            messagebox.showwarning("No Folder", "Please select a folder first using File > Open Folder")
            return
        
        # Create progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Finding Duplicates...")
        progress_window.geometry("400x100")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        tk.Label(progress_window, text="Scanning files for duplicates...", font=("Arial", 12)).pack(pady=20)
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill='x')
        progress_bar.start()
        
        # Update the UI
        progress_window.update()
        
        try:
            # Find duplicates
            duplicates, total_files = self.file_handler.find_duplicate_images()
            progress_bar.stop()
            progress_window.destroy()
            
            if duplicates is None:
                messagebox.showerror("Error", f"Error finding duplicates: {total_files}")
                return
            
            if not duplicates:
                messagebox.showinfo("No Duplicates", f"No duplicate images found in {total_files} files.")
                return
            
            # Show duplicate management dialog
            self.show_duplicate_management_dialog(duplicates, total_files)
            
        except Exception as e:
            progress_bar.stop()
            progress_window.destroy()
            messagebox.showerror("Error", f"Error finding duplicates: {e}")
    
    def show_duplicate_management_dialog(self, duplicates, total_files):
        """Show dialog to manage found duplicates"""
        duplicate_count = sum(len(files) for files in duplicates.values())
        unique_folders = self.file_handler.get_unique_folders(duplicates)
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Duplicate Files")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Info label
        info_text = f"Found {duplicate_count} duplicate files in {len(duplicates)} groups.\nTotal files scanned: {total_files}"
        tk.Label(dialog, text=info_text, font=("Arial", 12), fg="blue").pack(pady=10)
        
        # Instructions
        tk.Label(dialog, text="Select folders to KEEP files from:", font=("Arial", 11, "bold")).pack(pady=(20, 5))
        tk.Label(dialog, text="(Duplicates from unselected folders will be deleted)", font=("Arial", 9), fg="red").pack()
        
        # Checkboxes for folders
        checkbox_frame = tk.Frame(dialog)
        checkbox_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        folder_vars = {}
        for folder in unique_folders:
            var = tk.BooleanVar(value=True)  # Default to keep all
            folder_vars[folder] = var
            cb = tk.Checkbutton(checkbox_frame, text=folder, variable=var, font=("Arial", 10))
            cb.pack(anchor='w', pady=2)
        
        # Details section
        details_frame = tk.LabelFrame(dialog, text="Duplicate Groups Preview", font=("Arial", 10))
        details_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Scrollable text widget
        text_frame = tk.Frame(details_frame)
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        text_widget = tk.Text(text_frame, height=8, font=("Arial", 9))
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Show duplicate details (limited to first few groups)
        preview_count = 0
        for hash_val, files in list(duplicates.items())[:5]:  # Show first 5 groups
            preview_count += 1
            text_widget.insert(tk.END, f"Group {preview_count}:\n")
            for file_path in files:
                folder_name = "Main Folder" if file_path.parent == self.file_handler.source_folder else str(file_path.parent.relative_to(self.file_handler.source_folder))
                text_widget.insert(tk.END, f"  • {file_path.name} (in {folder_name})\n")
            text_widget.insert(tk.END, "\n")
        
        if len(duplicates) > 5:
            text_widget.insert(tk.END, f"... and {len(duplicates) - 5} more duplicate groups")
        
        text_widget.config(state='disabled')
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def remove_duplicates():
            selected_folders = [folder for folder, var in folder_vars.items() if var.get()]
            if not selected_folders:
                messagebox.showwarning("No Selection", "Please select at least one folder to keep files from.")
                return
            
            result = messagebox.askyesno("Confirm Deletion", 
                f"This will permanently delete duplicate files from folders NOT selected.\n\n"
                f"Files will be kept from: {', '.join(selected_folders)}\n\n"
                f"Are you sure you want to continue?")
            
            if result:
                success, message = self.file_handler.remove_duplicates(duplicates, selected_folders)
                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", message)
        
        tk.Button(button_frame, text="Remove Duplicates", command=remove_duplicates, 
                 bg="#ff4444", fg="white", font=("Arial", 11, "bold")).pack(side='left', padx=10)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, 
                 font=("Arial", 11)).pack(side='left', padx=10)
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    folder_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = ImageSorter(folder_path)
    app.run()