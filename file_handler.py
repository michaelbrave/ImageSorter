import os
import shutil
from pathlib import Path
from send2trash import send2trash


class FileHandler:
    def __init__(self, source_folder, search_subfolders=False):
        self.source_folder = Path(source_folder)
        self.search_subfolders = search_subfolders
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}
        
    def get_image_files(self):
        image_files = []
        if self.search_subfolders:
            for file_path in self.source_folder.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.image_extensions:
                    image_files.append(file_path)
        else:
            for file_path in self.source_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.image_extensions:
                    image_files.append(file_path)
        return sorted(image_files)
    
    def move_to_folder(self, file_path, folder_name):
        try:
            source_path = Path(file_path)
            
            if self.search_subfolders and source_path.parent != self.source_folder:
                destination_folder = self.source_folder / folder_name
            else:
                destination_folder = source_path.parent / folder_name
                
            destination_folder.mkdir(exist_ok=True)
            
            destination_path = destination_folder / source_path.name
            
            if destination_path.exists():
                counter = 1
                stem = source_path.stem
                suffix = source_path.suffix
                while destination_path.exists():
                    destination_path = destination_folder / f"{stem}_{counter}{suffix}"
                    counter += 1
            
            shutil.move(str(source_path), str(destination_path))
            return True, f"Moved to {destination_path}"
            
        except Exception as e:
            return False, f"Error moving file: {e}"
    
    def send_to_recycle(self, file_path):
        try:
            send2trash(str(file_path))
            return True, "Sent to recycle bin"
        except Exception as e:
            return False, f"Error sending to recycle bin: {e}"
    
    def process_action(self, file_path, action):
        if action["type"] == "folder":
            return self.move_to_folder(file_path, action["name"])
        elif action["type"] == "recycle":
            return self.send_to_recycle(file_path)
        else:
            return False, f"Unknown action type: {action['type']}"