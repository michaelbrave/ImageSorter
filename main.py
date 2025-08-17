#!/usr/bin/env python3

import sys
from pathlib import Path
from image_sorter import ImageSorter


def main():
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        if not Path(folder_path).exists():
            print(f"Error: Folder '{folder_path}' does not exist.")
            sys.exit(1)
    else:
        folder_path = None
    
    try:
        app = ImageSorter(folder_path)
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()