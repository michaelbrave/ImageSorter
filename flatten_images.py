#!/usr/bin/env python3
"""
Script to move all images from subfolders to their parent folders
and remove empty subfolders.
"""

import os
import shutil
from pathlib import Path

# Common image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
                   '.webp', '.svg', '.ico', '.heic', '.heif', '.raw', '.cr2',
                   '.nef', '.arw', '.dng'}

def is_image_file(filename):
    """Check if a file is an image based on its extension."""
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS

def move_images_from_subfolders(root_dir):
    """
    Move all images from subfolders to their parent folder.

    Args:
        root_dir: The root directory to process
    """
    root_path = Path(root_dir).resolve()

    if not root_path.exists():
        print(f"Error: Directory '{root_dir}' does not exist")
        return

    if not root_path.is_dir():
        print(f"Error: '{root_dir}' is not a directory")
        return

    print(f"Processing: {root_path}")
    print("-" * 80)

    # Walk through all subdirectories
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        current_dir = Path(dirpath)

        # Skip if this is the root directory
        if current_dir == root_path:
            continue

        # Get the parent directory
        parent_dir = current_dir.parent

        # Process all image files in this directory
        images_moved = 0
        for filename in filenames:
            if is_image_file(filename):
                source = current_dir / filename
                destination = parent_dir / filename

                # Handle filename conflicts
                if destination.exists():
                    # Add a number suffix to make it unique
                    base_name = destination.stem
                    extension = destination.suffix
                    counter = 1
                    while destination.exists():
                        destination = parent_dir / f"{base_name}_{counter}{extension}"
                        counter += 1

                try:
                    shutil.move(str(source), str(destination))
                    print(f"Moved: {source.relative_to(root_path)} -> {destination.relative_to(root_path)}")
                    images_moved += 1
                except Exception as e:
                    print(f"Error moving {source}: {e}")

        # After moving images, check if directory is empty and remove it
        try:
            if not any(current_dir.iterdir()):
                current_dir.rmdir()
                print(f"Removed empty folder: {current_dir.relative_to(root_path)}")
            elif images_moved > 0:
                # Directory still has non-image files
                remaining = list(current_dir.iterdir())
                print(f"Note: {current_dir.relative_to(root_path)} still contains {len(remaining)} non-image file(s)")
        except OSError as e:
            print(f"Could not remove {current_dir}: {e}")

    print("-" * 80)
    print("Done!")

def main():
    import sys

    # Get target directory from command line or use current directory
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = input("Enter the directory path to process (or press Enter for current directory): ").strip()
        if not target_dir:
            target_dir = "."

    move_images_from_subfolders(target_dir)

if __name__ == "__main__":
    main()
