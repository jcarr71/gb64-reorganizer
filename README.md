# GameBase64 Game Organizer

A Python utility to organize Commodore 64 games from zip archives into a structured folder hierarchy based on metadata from VERSION.NFO files.

## Features

- **Automatic Organization**: Extracts games from zip files and organizes them into a clean folder structure
- **Metadata-Based Sorting**: Uses VERSION.NFO files to categorize games by:
  - Primary Genre
  - Secondary Genre
  - Language
- **Smart Disk File Handling**: Automatically detects and renames Commodore 64 disk files (D64, D71, D81, G64, X64, T64, TAP, PRG, P00, LNX)
- **Duplicate Handling**: Automatically versioning for duplicate game names
- **Error Reporting**: Detailed logging of skipped games and errors

## Requirements

- Python 3.6+
- No external dependencies required (uses only Python standard library)
- **GameBase64 games library** installed on your system

## Installation

### Option 1: Run from Python

1. Clone or download this repository
2. Ensure Python 3.6+ is installed on your system
3. Have your GameBase64 games library ready (this tool organizes games from it)
4. Run: `python gb64_reorganizer.py`

### Option 2: Use the Executable

Download the pre-built executable from the [Releases](../../releases) page and run it directly—no Python installation needed!

## Building the Executable

If you want to build your own executable:

1. Install PyInstaller: `pip install pyinstaller`
2. Run the build script: `./build.ps1` (Windows PowerShell)
3. The executable will be created in the `dist/` folder

Or build manually:
```bash
pyinstaller --onefile --windowed --name C64GameOrganizer gb64_reorganizer.py
```

## Usage

### From Command Line (Python)

```bash
python gb64_reorganizer.py
```

### From Executable

Simply double-click `C64GameOrganizer.exe` in the `dist/` folder.

### Input Prompts

The program will prompt you for:

1. **Source Directory**: Path to your GameBase64 games folder (the one containing all the zipped game files)
2. **Destination Directory**: Path where you want the organized games to be placed

### Example

If your GameBase64 library is located at `D:\GameBase64\Games\`, you would enter that as your source directory.

### Example Folder Structure

After running the organizer, your games will be organized like this:

```
destination_directory/
├── Action/
│   ├── Shooter/
│   │   ├── English/
│   │   │   ├── Galaxian/
│   │   │   └── Pac-Man/
│   │   └── German/
│   │       └── Space Invaders/
├── Adventure/
│   ├── Text Adventure/
│   │   └── English/
│   │       └── Zork/
└── Puzzle/
    ├── Match-3/
    │   └── English/
    │       └── Tetris/
```

## How It Works

1. **Zip Extraction**: Extracts each zip file to a temporary directory
2. **Metadata Parsing**: Reads VERSION.NFO file to extract game information
3. **Organization**: Creates folder hierarchy based on Genre/Subgenre/Language
4. **Disk File Handling**: Renames game disk files with standard extensions
5. **Cleanup**: Removes temporary files after processing

## Notes

- Games are **copied** to the destination directory (originals are preserved)
- Invalid Windows filename characters are automatically removed
- Duplicate game names are automatically versioned (e.g., `GameName [v2]`, `GameName [v3]`)
- Processing progress is displayed in the console with status indicators
