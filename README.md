# Image Sorter

A Tinder-style image sorting application built with Python and tkinter. Quickly sort images using arrow keys to organize them into custom folders or send them to the recycle bin.

## Features

- **Intuitive Controls**: Use arrow keys to sort images quickly
- **Customizable Actions**: Map each direction to custom folder names or recycle bin
- **Visual Feedback**: On-screen indicators show current action mappings
- **Subfolder Search**: Option to include images from subdirectories
- **Progress Tracking**: See current image number and total count
- **Persistent Settings**: Configuration saved between sessions
- **Duplicate Detection**: Find and manage duplicate images across all folders
- **Empty Folder Cleanup**: Automatically remove empty subfolders after sorting
- **Editable Action Names**: Double-click action labels to rename sorting categories

## Installation

1. **Clone or download** this repository to your local machine

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python main.py
```

Or run directly without arguments:
```bash
# Activate virtual environment and run in one command
source venv/bin/activate && python main.py
```

### Using the Application

1. **Select a folder**: Use `File > Open Folder` to choose a directory containing images
2. **Enable subfolder search** (optional): Check `File > Search Subfolders` to include images in subdirectories
3. **Sort images**: Use arrow keys to sort the current image:
   - **↑ (Up)**: Move to "Manybe" folder
   - **↓ (Down)**: Send to recycle bin
   - **← (Left)**: Move to "Core" folder  
   - **→ (Right)**: Move to "Scraps" folder
4. **Navigate**: 
   - **Space**: Next image (without sorting)
   - **Backspace**: Previous image
   - **Escape**: Exit application

### Advanced Features

#### Customizing Action Names
- **Double-click** any action label (↑, ↓, ←, →) to rename the sorting category
- Names are automatically saved and persist between sessions
- Use descriptive names like "Keep", "Delete", "Maybe", "Archive", etc.

#### Managing Duplicates
1. Go to `Edit > Find Duplicates...` to scan for duplicate images
2. The system searches all folders and subfolders automatically
3. Select which folders to **keep** files from using checkboxes
4. Duplicates from unselected folders will be safely moved to recycle bin
5. Preview shows duplicate groups with their locations

#### Empty Folder Cleanup
- After completing image sorting with subfolder search enabled
- Click the **"🗑️ Clean Up Empty Subfolders"** button that appears
- Safely removes any empty directories left behind after moving images

### Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## Configuration

The application creates a `config.json` file to store your preferences:

- **Action mappings**: Customize what each arrow key does
- **Window settings**: Size and appearance preferences
- **Subfolder search**: Remember your search preference

## File Organization

### Basic Sorting
When you sort images, the application:
- Creates subfolders in the source directory as needed
- Moves images to the appropriate subfolder based on your choice
- Handles filename conflicts by adding numbers (e.g., `image_1.jpg`)
- Sends images to the system recycle bin when using the down arrow

### Subfolder Mode
When "Search Subfolders" is enabled:
- **Sorting**: All images from subfolders are moved to new folders in the root directory
- **Organization**: Original subfolder structure is preserved until cleanup
- **Safety**: Empty subfolders can be cleaned up after sorting is complete

### Duplicate Management
The duplicate detection system:
- Uses MD5 hash comparison for accurate duplicate identification
- Always searches all folders and subfolders regardless of search settings
- Allows selective removal based on folder location preferences
- Safely moves unwanted duplicates to recycle bin

## Troubleshooting

### Virtual Environment Issues
If you encounter permission errors, make sure you're using the virtual environment:
```bash
source venv/bin/activate
```

### Missing Dependencies
If you get import errors, reinstall dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### No Images Found
- Check that your folder contains supported image formats
- Try enabling "Search Subfolders" if images are in subdirectories
- Verify file permissions allow reading the images

### Duplicate Detection Issues
- Large folders may take time to scan - be patient during the scanning process
- If duplicate detection fails, check file permissions and available disk space
- MD5 calculation requires reading entire files, so scanning is slower for large images

### Empty Folder Cleanup
- The cleanup button only appears after completing all sorting when using subfolder mode
- Only completely empty folders are removed for safety
- If folders won't delete, check for hidden files or permission issues

## Development

The application consists of several modules:

- `main.py`: Entry point
- `image_sorter.py`: Main application class with UI
- `config_manager.py`: Configuration handling
- `file_handler.py`: File operations and image discovery
- `config.json`: User settings (created at runtime)

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- Pillow (PIL) for image processing
- send2trash for cross-platform recycle bin support