# Copilot Instructions - GameBase64 Game Organizer

## Project Overview

This is a single-file Python utility that organizes Commodore 64 games from zip archives into a structured folder hierarchy. The tool:
- Extracts zip files containing games
- Parses VERSION.NFO metadata files for game information (name, genre, language)
- Creates folder structure: `PrimaryGenre/SecondaryGenre/Language/GameName/`
- Handles disk file renaming for multi-disk games
- Provides comprehensive logging and error reporting

**Key insight**: This is a metadata extraction and file organization tool, not a game emulator or runtime system.

## Architecture & Components

### Core Class: `C64GameOrganizer`
Located in [gb64_reorganizer.py](../gb64_reorganizer.py), this single class encapsulates the entire workflow:

1. **Initialization** (lines 37-50): Accepts source/destination paths, initializes counters for tracking progress
2. **Zip Extraction** (lines 51-67): Extracts to temporary directory using Python's `tempfile` module
3. **Metadata Parsing** (lines 70-144): Parses VERSION.NFO files using regex patterns to extract Name, Genre (primary/secondary split on " - "), and Language
4. **File Organization** (lines 198-254): Core workflow - processes zips, validates metadata, creates folder structure, handles duplicates
5. **Disk File Handling** (lines 163-190): Renames multi-disk files (d64, d71, d81, g64, x64, t64, tap, prg, p00, lnx) to `gamename_d1`, `gamename_d2`, etc.
6. **Zip Processing** (lines 256-313): Main worker method that orchestrates extraction, parsing, sanitization, and organization

### Data Flow
```
User Input → Scan source dir for *.zip files 
→ Extract to temp → Find VERSION.NFO 
→ Parse metadata (regex) → Sanitize filenames 
→ Rename disk files → Copy to dest structure 
→ Handle duplicates (version numbering) → Log results
```

## Critical Developer Workflows

### Building the Executable
Run `./build.ps1` (Windows PowerShell required). This:
1. Checks for PyInstaller, installs if missing
2. Calls `pyinstaller --onefile --name GB64GameOrganizer gb64_reorganizer.py`
3. Outputs to `./dist/GB64GameOrganizer.exe`
4. Configuration file `GB64GameOrganizer.spec` contains PyInstaller build metadata

### Testing & Local Development
- Run directly: `python gb64_reorganizer.py`
- Program uses `move_files=False` by default (copies not moves) - safe for testing
- Output: `organization_log.txt` in destination directory with detailed processing log (also mirrors output to console)
- Temporary files automatically cleaned via `shutil.rmtree()` in finally block (guaranteed cleanup even on errors)
- **Safe mode**: Program never modifies source zips - it only copies/moves the organized game folders
- Test with small subsets of zips first to validate metadata parsing before processing entire libraries

## Project-Specific Patterns & Conventions

### Pattern 1: Regex-Based Metadata Parsing
The VERSION.NFO parser (lines 70-144) uses specific regex patterns:
- **Multi-line fields**: Uses `re.DOTALL` flag to capture Genre across multiple lines
- **Line anchors**: `^\s*Name:` to match field at line start
- **Fallback logic**: If GAME INFO section not found, searches entire content
- **Safe defaults**: Language defaults to "(No Text)" if not found

### Pattern 2: Sanitization for Windows Compatibility
Two-step sanitization (lines 192-207):
1. Remove Windows-invalid chars: `<>:"|?*`
2. Strip leading/trailing spaces and dots: `strip('. ')`
Applied to: game names, primary genre, secondary genre, language

### Pattern 3: Duplicate Handling with Version Numbering
When destination folder exists (lines 283-289):
- Append `[v2]`, `[v3]`, etc. to game name
- Loop until unique path found
- All duplicate info logged as errors for user transparency

### Pattern 4: Explicit File Operation Safety
- Zip extraction → temporary directory (not in-place)
- Copy operations (not move) by default via `shutil.copytree()`
- Cleanup in finally block guarantees temp cleanup even on errors
- No destructive operations on source files

## Key Dependencies & External Integration

- **No external dependencies**: Uses only Python standard library
  - `pathlib.Path` for cross-platform paths
  - `zipfile` for extraction
  - `tempfile.mkdtemp()` for safe temporary directories
  - `shutil` for copying/removing directories
  - `re` for regex parsing
  - `typing` for type hints

- **GameBase64 expectation**: Source directory must contain .zip files with VERSION.NFO inside

- **Windows compatibility**: Uses `shutil` cross-platform APIs and regex patterns designed for Windows filenames

## Important Implementation Details

1. **Genre splitting** (line 110): Only splits primary/secondary if " - " separator exists, otherwise primary_genre gets full text and secondary_genre defaults to "Other"

2. **NFO recursive search** (lines 117-124): Searches entire extracted folder tree recursively - handles nested folder structures where VERSION.NFO may be in subdirectories

3. **Disk file ordering** (line 175): Files sorted before renaming ensures consistent d1, d2, d3 ordering across runs

4. **Progress output**: Uses emoji indicators in console output (✓, ✗, ⚠) for visual scanning of results and errors

5. **Logging**: Creates `organization_log.txt` in destination directory with duplicate of console output - enables reviewing results after completion

6. **Error collection strategy** (lines 37, 45, 94, 102): Uses `self.errors` list to collect all issues (metadata failures, missing NFO, duplicates) and displays them at end of run - provides complete failure audit trail

7. **Null safety in parsing**: `parse_version_nfo()` returns `None` on any parsing failure; this triggers graceful skip with detailed error rather than crashing

## Common Modifications

- Adding new disk file extensions: Edit `disk_extensions` set in `rename_disk_files()` (line 170)
- Changing folder structure: Modify destination path construction (line 266)
- Supporting additional metadata fields: Extend `parse_version_nfo()` regex patterns
- Customizing error handling: Modify exception handlers in try/finally blocks
