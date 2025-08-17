import tkinter as tk
from tkinter import messagebox, filedialog, Menu, simpledialog
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
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    folder_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = ImageSorter(folder_path)
    app.run()