# GameBase Game Organizer

A Python utility to organize retro game collections (Commodore 64, Amiga, etc.) from zip archives into a structured folder hierarchy based on metadata extracted from VERSION.NFO files.

## Version Info

**Current Stable Release:** v1.2.0 (CLI only)
**GUI Status:** Work in Progress (Experimental)

👉 **Recommended:** Use the CLI (`gb64_reorganizer.py`) for production use

## Features (CLI - v1.2.0 Stable)

- ✅ **Automatic Organization**: Extracts games from zip files and organizes them into a clean folder structure
- ✅ **Metadata-Based Sorting**: Extracts metadata from VERSION.NFO files (15+ fields):
  - Primary Genre, Secondary Genre, Language
  - Published Year, Publisher, Developer
  - Players, Control, PAL/NTSC
  - Unique ID, Coding/Graphics/Music Credits, Comments
- ✅ **Customizable Templates**: Define your own folder structure using 15 field placeholders
- ✅ **Path Sanitization**: Handles special characters in metadata (e.g., "English \ Italian")
- ✅ **Template Validation**: Helpful error messages for typos
- ✅ **Smart Disk File Handling**: Automatically detects and renames disk files (D64, D71, D81, G64, X64, T64, TAP, PRG, P00, LNX)
- ✅ **Duplicate Handling**: Automatic versioning for duplicate game names
- ✅ **Error Reporting**: Detailed logging of skipped games and errors

## Experimental Features (GUI - Work in Progress)

⚠️ **Warning:** The GUI is experimental and not recommended for large collections yet.

- 🧪 Interactive interface with game preview
- 🧪 Progress tracking and cancellation
- 🧪 Metadata caching (may have bugs)
- 🧪 Filtering by genre/language/publisher
- 🧪 Selective organization with checkboxes

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
3. **Folder Template** (optional): Customize how games are organized using field placeholders

### Customizing Organization

The organizer supports flexible folder templates with 15 available field placeholders:

**Available Fields**: `{name}`, `{primary_genre}`, `{secondary_genre}`, `{language}`, `{published_year}`, `{publisher}`, `{developer}`, `{players}`, `{control}`, `{pal_ntsc}`, `{unique_id}`, `{coding}`, `{graphics}`, `{music}`, `{comment}`

**Example Templates**:
- `{primary_genre}/{secondary_genre}/{language}/{name}` (default)
- `{published_year}/{primary_genre}/{name}` (organize by release year)
- `{publisher}/{name}` (organize by publisher)
- `{unique_id}/{name}` (organize by GameBase ID)

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

## Metadata Extraction

The organizer extracts metadata from VERSION.NFO files embedded in each game zip file, including:

- **Game Name**: The title of the game
- **Genres**: Primary and secondary genre categories
- **Language**: Text language of the game
- **Year**: Published year
- **Publisher**: Publishing company
- **Developer**: Development studio
- **Credits**: Coding, graphics, and music contributors
- **Technical Info**: Player count, control type, PAL/NTSC format

If VERSION.NFO metadata is missing or incomplete, the organizer uses the zip filename as a fallback.

## How It Works

1. **Zip Extraction**: Extracts each zip file to a temporary directory
2. **Metadata Extraction**: Reads VERSION.NFO file for game information
3. **Organization**: Creates folder hierarchy based on your template
4. **Disk File Handling**: Renames game disk files with standardized naming
5. **Cleanup**: Removes temporary files after processing

## Notes

- Games are **copied** to the destination directory (originals are preserved)
- Zero external Python dependencies (uses only standard library)
- Invalid Windows filename characters are automatically removed
- Duplicate game names are automatically versioned (e.g., `GameName [v2]`, `GameName [v3]`)
- Processing progress is displayed in the console with status indicators
- Customizable folder templates support 15 different metadata fields
