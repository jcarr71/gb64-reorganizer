# GameBase64 Game Organizer

A Python utility to organize Commodore 64 games from zip archives into a structured folder hierarchy based on metadata from VERSION.NFO files or SQLite/MDB databases.

## Features

- **Automatic Organization**: Extracts games from zip files and organizes them into a clean folder structure
- **Metadata-Based Sorting**: Uses VERSION.NFO files, SQLite databases, or MDB databases to categorize games by:
  - Primary Genre
  - Secondary Genre
  - Language
  - Year
  - Publisher
- **SQLite Database Support**: Download game databases directly from GitHub (no external dependencies!)
- **Smart Disk File Handling**: Automatically detects and renames Commodore 64 disk files (D64, D71, D81, G64, X64, T64, TAP, PRG, P00, LNX)
- **Duplicate Handling**: Automatically versioning for duplicate game names
- **Error Reporting**: Detailed logging of skipped games and errors
- **Modern GUI**: Interactive interface with game preview, filtering, and GitHub database downloads

## Requirements

- Python 3.7+
- No external dependencies required (uses only Python standard library)
- **GameBase64 games library** installed on your system

## Installation

### Option 1: Run from Python

1. Clone or download this repository
2. Ensure Python 3.7+ is installed on your system
3. Have your GameBase64 games library ready (this tool organizes games from it)
4. Run: `python gb64_reorganizer.py` (CLI) or `python gb64_gui.py` (GUI)

### Option 2: Use the Executable

Download the pre-built executable (GB64GameOrganizer.exe) from the [Releases](../../releases) page and run it directly—no Python installation needed!

## Building the Executable

If you want to build your own executable:

1. Install PyInstaller: `pip install pyinstaller`
2. Run the build script: `./build.ps1` (Windows PowerShell)
3. The executable will be created in the `dist/` folder

Or build manually:
```bash
pyinstaller --onefile --name GB64GameOrganizer gb64_reorganizer.py
```

## Usage

### From Command Line (Python - CLI)

```bash
python gb64_reorganizer.py
```

### From Command Line (Python - GUI)

```bash
python gb64_gui.py
```

### From Executable

Simply double-click `GB64GameOrganizer.exe` in the `dist/` folder.

### Input Prompts (CLI)

The program will prompt you for:

1. **Source Directory**: Path to your GameBase64 games folder (the one containing all the zipped game files)
2. **Destination Directory**: Path where you want the organized games to be placed
3. **SQLite Database** (optional): Use a SQLite database file for enhanced metadata lookup

### Database Options

The organizer supports multiple metadata sources (tried in this order):

1. **SQLite Database** (recommended)
   - Modern, portable format
   - Download directly from GitHub
   - No external dependencies
   - See [SQLITE_SETUP.md](SQLITE_SETUP.md) for details

2. **VERSION.NFO Files** (always available)
   - Embedded in game zip files
   - Basic metadata: Name, Genre, Language
   - Automatic fallback if database not available

3. **Legacy MDB/CSV Databases** (deprecated)
   - Requires Access Database Engine installation
   - Limited support
   - Use SQLite instead for better portability

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

## Database Setup

### Using SQLite (Recommended)

For the best experience with enhanced metadata, use a SQLite database:

1. **Download from GitHub** (easiest):
   - GUI: Click "Browse or Download..." → Select "NO" to download
   - Provide your GitHub repository information
   - Database is automatically downloaded and loaded

2. **Use a local SQLite file**:
   - CLI: Run the program and provide path when prompted
   - GUI: Click "Browse or Download..." → Select "YES" → Select `.db` file

3. **Convert your MDB database**:
   - See [SQLITE_SETUP.md](SQLITE_SETUP.md) for conversion instructions

### Without a Database

If no database is available, the organizer falls back to VERSION.NFO metadata embedded in each game zip file. This provides basic information (name, primary genre, language) automatically.

## How It Works

1. **Zip Extraction**: Extracts each zip file to a temporary directory
2. **Metadata Lookup**: Tries database first, then VERSION.NFO as fallback
3. **Organization**: Creates folder hierarchy based on Genre/Subgenre/Language
4. **Disk File Handling**: Renames game disk files with standard extensions
5. **Cleanup**: Removes temporary files after processing

## Notes

- Games are **copied** to the destination directory (originals are preserved)
- SQLite databases can be version-controlled in GitHub for easy sharing
- Zero external Python dependencies when using SQLite mode
- Invalid Windows filename characters are automatically removed
- Duplicate game names are automatically versioned (e.g., `GameName [v2]`, `GameName [v3]`)
- Processing progress is displayed in the console with status indicators
