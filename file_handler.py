import os
import shutil
import hashlib
from pathlib import Path
from send2trash import send2trash
from collections import defaultdict


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
            
            # Always move to root folder when search_subfolders is enabled
            if self.search_subfolders:
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
            
        except PermissionError as e:
            return False, f"Permission denied moving file: {source_path.name} - {e}"
        except FileNotFoundError as e:
            return False, f"File not found: {source_path.name} - {e}"
        except OSError as e:
            return False, f"OS error moving file: {source_path.name} - {e}"
        except Exception as e:
            return False, f"Unexpected error moving file: {source_path.name} - {e}"
    
    def send_to_recycle(self, file_path):
        try:
            send2trash(str(file_path))
            return True, "Sent to recycle bin"
        except Exception as e:
            return False, f"Error sending to recycle bin: {e}"
    
    def remove_empty_subfolders(self):
        """Remove empty subfolders from the source directory"""
        try:
            removed_folders = []
            
            # Walk through all subdirectories, bottom-up to handle nested empty folders
            for root, dirs, files in os.walk(self.source_folder, topdown=False):
                for directory in dirs:
                    folder_path = Path(root) / directory
                    
                    # Skip if this is the source folder itself
                    if folder_path == self.source_folder:
                        continue
                    
                    try:
                        # Check if folder is empty (no files or subdirectories)
                        if not any(folder_path.iterdir()):
                            folder_path.rmdir()
                            removed_folders.append(str(folder_path.relative_to(self.source_folder)))
                    except OSError:
                        # Folder not empty or permission issue, skip
                        continue
            
            if removed_folders:
                return True, f"Removed {len(removed_folders)} empty folders: {', '.join(removed_folders)}"
            else:
                return True, "No empty subfolders found to remove"
                
        except Exception as e:
            return False, f"Error removing empty folders: {e}"
    
    def get_file_hash(self, file_path):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def find_duplicate_images(self):
        """Find duplicate images in the source folder and all subfolders (always recursive)"""
        try:
            file_hashes = defaultdict(list)
            all_image_files = []
            
            # Always get all image files including subfolders for duplicate detection
            for file_path in self.source_folder.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.image_extensions:
                    all_image_files.append(file_path)
            
            # Calculate hashes for all files
            for file_path in all_image_files:
                file_hash = self.get_file_hash(file_path)
                if file_hash:
                    file_hashes[file_hash].append(file_path)
            
            # Find duplicates (hashes with more than one file)
            duplicates = {hash_val: files for hash_val, files in file_hashes.items() if len(files) > 1}
            
            return duplicates, len(all_image_files)
            
        except Exception as e:
            return None, f"Error finding duplicates: {e}"
    
    def get_unique_folders(self, duplicate_files):
        """Get list of unique folders containing duplicate files"""
        folders = set()
        for files in duplicate_files.values():
            for file_path in files:
                if file_path.parent == self.source_folder:
                    folders.add("Main Folder")
                else:
                    folders.add(str(file_path.parent.relative_to(self.source_folder)))
        return sorted(list(folders))
    
    def remove_duplicates(self, duplicates, folders_to_keep):
        """Remove duplicate files, keeping only those in specified folders"""
        try:
            removed_files = []
            kept_files = []
            
            for hash_val, files in duplicates.items():
                files_to_keep = []
                files_to_remove = []
                
                # Categorize files based on folder preference
                for file_path in files:
                    if file_path.parent == self.source_folder:
                        folder_name = "Main Folder"
                    else:
                        folder_name = str(file_path.parent.relative_to(self.source_folder))
                    
                    if folder_name in folders_to_keep:
                        files_to_keep.append(file_path)
                    else:
                        files_to_remove.append(file_path)
                
                # If no files are in keep folders, keep the first one
                if not files_to_keep and files_to_remove:
                    files_to_keep.append(files_to_remove.pop(0))
                
                # Remove duplicate files
                for file_path in files_to_remove:
                    try:
                        send2trash(str(file_path))
                        removed_files.append(file_path.name)
                    except Exception as e:
                        continue
                
                kept_files.extend([f.name for f in files_to_keep])
            
            return True, f"Removed {len(removed_files)} duplicate files. Kept {len(kept_files)} files."
            
        except Exception as e:
            return False, f"Error removing duplicates: {e}"
    
    def move_images_to_main_folder(self):
        """Move all images from subfolders to the main source folder"""
        try:
            moved_count = 0
            removed_folders = []

            # Walk through all subdirectories
            for dirpath, dirnames, filenames in os.walk(self.source_folder, topdown=False):
                current_dir = Path(dirpath)

                # Skip if this is the source folder itself
                if current_dir == self.source_folder:
                    continue

                # Process all image files in this directory
                for filename in filenames:
                    if Path(filename).suffix.lower() in self.image_extensions:
                        source = current_dir / filename
                        destination = self.source_folder / filename

                        # Handle filename conflicts
                        if destination.exists():
                            base_name = destination.stem
                            extension = destination.suffix
                            counter = 1
                            while destination.exists():
                                destination = self.source_folder / f"{base_name}_{counter}{extension}"
                                counter += 1

                        try:
                            shutil.move(str(source), str(destination))
                            moved_count += 1
                        except Exception as e:
                            print(f"Error moving {source}: {e}")
                            continue

                # After moving images, check if directory is empty and remove it
                try:
                    if not any(current_dir.iterdir()):
                        current_dir.rmdir()
                        removed_folders.append(str(current_dir.relative_to(self.source_folder)))
                except OSError:
                    # Directory not empty or permission issue, skip
                    continue

            result_message = f"Moved {moved_count} image(s) to main folder."
            if removed_folders:
                result_message += f"\nRemoved {len(removed_folders)} empty folder(s)."
            elif moved_count > 0:
                result_message += "\nSome subfolders still contain non-image files."

            return True, result_message

        except Exception as e:
            return False, f"Error moving images to main folder: {e}"

    def process_action(self, file_path, action):
        if action["type"] == "folder":
            return self.move_to_folder(file_path, action["name"])
        elif action["type"] == "recycle":
            return self.send_to_recycle(file_path)
        else:
            return False, f"Unknown action type: {action['type']}"