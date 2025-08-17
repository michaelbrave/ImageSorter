# Image Sorter - Implementation Plan

## Overview
A Tinder-style image sorting application using Python and tkinter. Users can quickly sort images using arrow keys to move them into custom folders or send to recycle bin.

## Core Features
- **Image Display**: Full-screen image viewer with automatic scaling
- **Keyboard Controls**: Arrow keys (↑↓←→) for sorting actions
- **Customizable Actions**: Map each direction to folder names or recycle bin
- **Visual Feedback**: On-screen indicators showing current action mappings
- **Progress Tracking**: Show current image number and total count

## Technical Architecture

### Dependencies
- **tkinter**: Built-in GUI framework
- **Pillow (PIL)**: Image loading and processing
- **send2trash**: Cross-platform recycle bin functionality
- **json**: Configuration persistence
- **pathlib**: Modern file path handling

### Core Components

#### 1. ImageSorter (Main Class)
- Initialize tkinter window
- Handle image loading and display
- Manage keyboard event binding
- Coordinate between UI and file operations

#### 2. ImageDisplay
- Scale images to fit window while maintaining aspect ratio
- Handle various image formats (JPEG, PNG, GIF, BMP, TIFF)
- Display current image with smooth transitions

#### 3. ConfigManager
- Load/save JSON configuration file
- Default mappings: ↑=Keep, ↓=Delete, ←=Folder1, →=Folder2
- Allow runtime configuration changes

#### 4. FileHandler
- Move images to designated folders
- Create folders if they don't exist
- Send files to recycle bin using send2trash
- Handle file operation errors gracefully

#### 5. UIOverlay
- Display current action mappings in corners/edges
- Show progress (current/total images)
- Display configuration panel when needed

## File Structure
```
ImageSorter/
├── plan.md
├── main.py              # Entry point
├── image_sorter.py      # Main application class
├── config_manager.py    # Configuration handling
├── file_handler.py      # File operations
├── ui_overlay.py        # UI elements and overlays
├── config.json          # User configuration (created at runtime)
└── requirements.txt     # Python dependencies
```

## Implementation Phases

### Phase 1: Core Image Display
- Create basic tkinter window
- Implement image loading with Pillow
- Add image scaling and centering
- Basic navigation (next/previous with Space/Backspace)

### Phase 2: Keyboard Controls
- Bind arrow key events
- Implement basic file moving functionality
- Add folder creation logic

### Phase 3: Configuration System
- JSON config file for action mappings
- Default configuration setup
- Runtime configuration changes

### Phase 4: UI Enhancements
- Action mapping display overlay
- Progress counter
- Error message display
- Configuration panel

### Phase 5: Polish & Testing
- Error handling for corrupted images
- Handle edge cases (empty folders, permission errors)
- Performance optimization for large image sets
- Cross-platform testing

## User Workflow
1. Run application with folder path as argument
2. View first image in fullscreen mode
3. See action mappings displayed on screen edges
4. Press arrow keys to sort current image
5. Application automatically moves to next image
6. Configure custom folder names via UI
7. Complete sorting session

## Configuration Format
```json
{
  "actions": {
    "up": {"type": "folder", "name": "Manybe"},
    "down": {"type": "recycle", "name": "Delete"},
    "left": {"type": "folder", "name": "Core"},
    "right": {"type": "folder", "name": "Scraps"}
  },
  "window": {
    "fullscreen": true,
    "background_color": "#000000"
  }
}
```

## Success Metrics
- Fast image sorting (< 2 seconds per image)
- Intuitive keyboard controls
- Reliable file operations with error recovery
- Cross-platform compatibility (Windows, macOS, Linux)
- Support for common image formats