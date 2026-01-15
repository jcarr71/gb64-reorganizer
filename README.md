# GameBase64 Game Organizer

A Python utility to organize GameBase64 game collections (Commodore 64, Amiga, etc.) from zip archives into a structured folder hierarchy based on metadata extracted from VERSION.NFO files.

## Version Info

**Current Stable Release:** v1.3.2 (CLI with extended options)
**GUI Status:** Work in Progress (Experimental)

👉 **Recommended:** Use the CLI (`gb64_reorganizer.py`) for production use

## Features (CLI - v1.3.2 Stable)

- ✅ **Automatic Organization**: Extracts games from zip files and organizes them into a clean folder structure
- ✅ **Metadata-Based Sorting**: Extracts metadata from VERSION.NFO files (15 fields):
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
- ✅ **English-Only Filter**: Optional filtering to process only English-language games
- ✅ **Publisher Simplification**: Strip publisher subtitles (e.g., "Publisher - Subsidiary" → "Publisher")
- ✅ **Keep Zipped Option**: Copy/move zip files without extracting (optional)

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

**Interactive mode** (prompts for all options):
```bash
python gb64_reorganizer.py
```

**Quick mode** (with basic arguments):
```bash
python gb64_reorganizer.py "C:\Source" "C:\Dest"
```

**With all options**:
```bash
python gb64_reorganizer.py "C:\Source" "C:\Dest" --template "{publisher}/{name}" --english-only --collapse-publishers --keep-zipped
```

### From Command Line (Python - GUI)

```bash
python gb64_gui.py
```

### From Executable

Simply double-click `GB64GameOrganizer.exe` in the `dist/` folder.

## Command-Line Options (CLI Only)

```
--template PATH_TEMPLATE
  Customize the folder structure (default: {primary_genre}/{secondary_genre}/{language}/{name})

--english-only
  Only process games with 'English' in the language field

--include-no-text
  When using --english-only, also include games with '(No Text)' language

--collapse-publishers
  Simplify publisher names by removing text after ' - ' separator
  Example: "Activision - Games" becomes "Activision"

--keep-zipped
  Copy/move zip files without extracting contents
  Useful for creating backups or archives
```

### Interactive Mode Options

If no arguments are provided, the program enters interactive mode and will ask you:

1. **Source Directory**: Path to your GameBase64 games folder (containing zipped games)
2. **Destination Directory**: Path where organized games will be placed
3. **Folder Template**: Customize how games are organized (or press Enter for default)
4. **English-Only Filter**: Process only games with English language
5. **Include (No Text) Filter**: When English-only is enabled, include games with no text
6. **Publisher Collapse**: Simplify publisher names
7. **Keep Zipped**: Keep files as zip archives instead of extracting

### Available Template Fields

Use any of these placeholders in your custom template:

```
{name}             - Game name
{primary_genre}    - Main game genre
{secondary_genre}  - Sub-genre
{language}         - Game language
{published_year}   - Release year
{publisher}        - Publisher name
{developer}        - Developer name
{players}          - Player count
{control}          - Control type
{pal_ntsc}         - Video format (PAL/NTSC)
{unique_id}        - GameBase unique ID
{coding}           - Coding credits
{graphics}         - Graphics credits
{music}            - Music credits
{comment}          - Comments/notes
```

**Example Templates**:
- `{primary_genre}/{secondary_genre}/{language}/{name}` (default - by genre and language)
- `{published_year}/{primary_genre}/{name}` (organize by release year then genre)
- `{publisher}/{name}` (organize by publisher)
- `{unique_id}/{name}` (organize by GameBase ID)
- `{language}/{publisher}/{primary_genre}/{name}` (organize by language, then publisher, then genre)
- `{name}` (flat structure with just game names)

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

- Games are **copied** to the destination directory by default (originals are preserved)
- Zero external Python dependencies (uses only standard library)
- Invalid Windows filename characters are automatically removed
- Duplicate game names are automatically versioned (e.g., `GameName [v2]`, `GameName [v3]`)
- Processing progress is displayed in the console with status indicators (✓ success, ✗ error, ⚠ warning)
- Full organization log is saved to `organization_log.txt` in the destination directory
- Temporary extraction folders are automatically cleaned up
- All operations are safe and non-destructive to source zip files

## Advanced Examples

### Organize by Year and Genre
```bash
python gb64_reorganizer.py "D:\GameBase64\Games" "D:\Organized Games" --template "{published_year}/{primary_genre}/{name}"
```

### Organize by Publisher (English Games Only)
```bash
python gb64_reorganizer.py "D:\GameBase64\Games" "D:\Organized Games" --template "{publisher}/{language}/{name}" --english-only --collapse-publishers
```

### Create Language-Organized Archive (Keep Zipped)
```bash
python gb64_reorganizer.py "D:\GameBase64\Games" "D:\Archived Games" --template "{language}/{primary_genre}/{name}" --keep-zipped
```

### Simple Flat Structure with Simplified Publisher Names
```bash
python gb64_reorganizer.py "D:\GameBase64\Games" "D:\Simple" --template "{name}" --collapse-publishers
```
