# Image Sorter

A Tinder-style image sorting application built with Python and tkinter. Quickly sort images using arrow keys to organize them into custom folders or send them to the recycle bin.

## Features

- **Intuitive Controls**: Use arrow keys to sort images quickly
- **Customizable Actions**: Map each direction to custom folder names or recycle bin
- **Visual Feedback**: On-screen indicators show current action mappings
- **Subfolder Search**: Option to include images from subdirectories
- **Progress Tracking**: See current image number and total count
- **Persistent Settings**: Configuration saved between sessions

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

When you sort images, the application:
- Creates subfolders in the source directory as needed
- Moves images to the appropriate subfolder based on your choice
- Handles filename conflicts by adding numbers (e.g., `image_1.jpg`)
- Sends images to the system recycle bin when using the down arrow

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