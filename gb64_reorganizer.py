#!/usr/bin/env python3
"""
GameBase64 Game Organizer

A utility to organize games from GameBase64 archives (Commodore 64, Amiga, etc.)
from zipped archives into a structured folder hierarchy based on metadata
extracted from VERSION.NFO files.

Version: 1.3.2
Author: Jason Carr
Date: January 2026
"""

from pathlib import Path
import shutil
import zipfile
import tempfile
import re
import argparse
from typing import Optional, Dict


class GamebaseOrganizer:
    """
    Organizes games from zipped archives into a structured folder hierarchy.
    
    Extracts games from zip files and creates folder structure:
    Destination/PrimaryGenre/SecondaryGenre/Language/GameName/
    
    Handles:
    - Zip file extraction to temporary directories
    - VERSION.NFO parsing for game metadata
    - Multi-line genre parsing with primary/secondary genre splitting
    - Disk file detection and renaming (D64, D71, D81, G64, X64, T64, TAP, PRG, P00, LNX)
    - Duplicate game handling with version numbering
    - Invalid Windows filename character removal
    """
    
    def __init__(self, source_dir: str, destination_dir: str):
        """
        Initialize the organizer with source and destination directories.
        
        Args:
            source_dir: Directory containing zip files of games
            destination_dir: Root directory where organized games will be placed
        """
        self.source_root = Path(source_dir)
        self.destination_root = Path(destination_dir)
        self.games_found = 0
        self.games_moved = 0
        self.errors = []
    
    def extract_zip_to_temp(self, zip_path: Path) -> Optional[Path]:
        """
        Extract a zip file to a temporary directory.
        
        Args:
            zip_path: Path to the zip file
            
        Returns:
            Path to temporary directory containing extracted files, or None if extraction failed
        """
        try:
            temp_dir = tempfile.mkdtemp(prefix='c64_game_')
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            return Path(temp_dir)
        except Exception as e:
            self.errors.append(f"Failed to extract {zip_path.name}: {str(e)}")
            return None
    
    def parse_version_nfo(self, nfo_path: Path) -> Optional[Dict[str, str | None]]:
        """
        Parse VERSION.NFO file and extract game metadata.
        
        Extracts: Name, Genre (primary/secondary), Language, Published, Players, Control, Pal/NTSC
        Genre format: "Primary - Secondary" (splits on dash)
        Published format: "YEAR Publisher" (splits on space)
        
        Args:
            nfo_path: Path to VERSION.NFO file
            
        Returns:
            Dictionary with keys: 'name', 'primary_genre', 'secondary_genre', 'language', 
                                 'published_year', 'publisher', 'players', 'control', 'pal_ntsc'
            Returns None if parsing fails
        """
        try:
            # Try multiple encodings without replacement first, then with replacement
            content = None
            
            # First pass: strict mode (no error replacement)
            for encoding in ['utf-8-sig', 'cp1252', 'latin-1']:
                try:
                    with open(nfo_path, 'r', encoding=encoding, errors='strict') as f:
                        content = f.read()
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            # Second pass: if strict failed, try with replacement
            if not content:
                for encoding in ['utf-8-sig', 'cp1252', 'latin-1']:
                    try:
                        with open(nfo_path, 'r', encoding=encoding, errors='replace') as f:
                            content = f.read()
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        continue
            
            if not content:
                return None
            
            # Find GAME INFO section
            game_info_match = re.search(r'GAME INFO(.*?)(?:GAME HISTORY|$)', content, re.DOTALL)
            if game_info_match:
                game_info = game_info_match.group(1)
            else:
                game_info = content
            
            # Extract Name field - specifically look for "Name:" at line start
            name_match = re.search(r'^\s*Name:\s*(.+?)$', game_info, re.MULTILINE)
            if not name_match:
                return None
            
            name = name_match.group(1).strip()
            
            # Extract Genre field (may span multiple lines)
            genre_match = re.search(r'Genre:\s*([^\n]+(?:\n\s+[^\n]+)*)', content, re.MULTILINE | re.DOTALL)
            if not genre_match:
                return None
            
            # Join multi-line genre and split on dash
            genre_text = re.sub(r'\s+', ' ', genre_match.group(1)).strip()
            
            if ' - ' in genre_text:
                primary_genre, secondary_genre = genre_text.split(' - ', 1)
                primary_genre = primary_genre.strip()
                secondary_genre = secondary_genre.strip()
            else:
                primary_genre = genre_text
                secondary_genre = 'Other'
            
            # Extract Language field
            lang_match = re.search(r'Language:\s*(.+?)$', content, re.MULTILINE)
            language = lang_match.group(1).strip() if lang_match else '(No Text)'
            
            # Extract Published field (format: "YEAR Publisher" or "YEAR Publisher Developer")
            published_year = 'Unknown'
            publisher = 'Unknown'
            pub_match = re.search(r'Published:\s*(.+?)$', content, re.MULTILINE)
            if pub_match:
                pub_text = pub_match.group(1).strip()
                # Split on first space to separate year from publisher
                parts = pub_text.split(None, 1)
                if len(parts) >= 1:
                    # Check if first part looks like a year (4 chars, digits and optional ?, like 198?)
                    first_part = parts[0]
                    if len(first_part) == 4 and all(c.isdigit() or c == '?' for c in first_part):
                        published_year = first_part
                        if len(parts) > 1:
                            publisher = parts[1]
                    else:
                        # If not a year, treat whole thing as publisher
                        publisher = pub_text
            
            # Extract Players field
            players = 'Unknown'
            players_match = re.search(r'Players:\s*(.+?)$', content, re.MULTILINE)
            if players_match:
                players = players_match.group(1).strip()
            
            # Extract Control field
            control = 'Unknown'
            control_match = re.search(r'Control:\s*(.+?)$', content, re.MULTILINE)
            if control_match:
                control = control_match.group(1).strip()
            
            # Extract Pal/NTSC field
            pal_ntsc = 'Unknown'
            pal_match = re.search(r'Pal/NTSC:\s*(.+?)$', content, re.MULTILINE)
            if pal_match:
                pal_ntsc = pal_match.group(1).strip()
            
            # Extract Unique-ID field
            unique_id = None
            id_match = re.search(r'Unique-ID:\s*(.+?)$', game_info, re.MULTILINE)
            if id_match:
                unique_id = id_match.group(1).strip()
            
            # Extract Developer field
            developer = None
            dev_match = re.search(r'Developer:\s*(.+?)$', game_info, re.MULTILINE)
            if dev_match:
                developer = dev_match.group(1).strip()
            
            # Extract Coding field
            coding = None
            coding_match = re.search(r'Coding:\s*(.+?)$', game_info, re.MULTILINE)
            if coding_match:
                coding = coding_match.group(1).strip()
            
            # Extract Graphics field
            graphics = None
            graphics_match = re.search(r'Graphics:\s*(.+?)$', game_info, re.MULTILINE)
            if graphics_match:
                graphics = graphics_match.group(1).strip()
            
            # Extract Music field
            music = None
            music_match = re.search(r'Music:\s*(.+?)$', game_info, re.MULTILINE)
            if music_match:
                music = music_match.group(1).strip()
            
            # Extract Comment field from GAME INFO section
            comment = None
            comment_match = re.search(r'Comment:\s*(.+?)$', game_info, re.MULTILINE)
            if comment_match:
                comment = comment_match.group(1).strip()
            
            return {
                'name': name,
                'primary_genre': primary_genre,
                'secondary_genre': secondary_genre,
                'language': language,
                'published_year': published_year,
                'publisher': publisher,
                'players': players,
                'control': control,
                'pal_ntsc': pal_ntsc,
                'unique_id': unique_id,
                'developer': developer,
                'coding': coding,
                'graphics': graphics,
                'music': music,
                'comment': comment
            }
        except Exception as e:
            self.errors.append(f"Failed to parse {nfo_path.name}: {str(e)}")
            return None
    
    
    def find_version_nfo(self, folder: Path) -> Optional[Path]:
        """
        Recursively search for VERSION.NFO file in a folder.
        
        Args:
            folder: Folder to search in
            
        Returns:
            Path to VERSION.NFO file, or None if not found
        """
        for nfo_file in folder.rglob('VERSION.NFO'):
            return nfo_file
        return None
    
    def rename_disk_files(self, folder: Path, game_name: str) -> None:
        """
        Rename multi-disk game files to standardized format (game_name_d1, game_name_d2, etc).
        
        Detects Commodore 64 disk file formats and renames them.
        Searches recursively through all subfolders.
        
        Args:
            folder: Game folder containing disk files
            game_name: Name of the game
        """
        # Disk file extensions for Commodore 64
        disk_extensions = {'.d64', '.d71', '.d81', '.g64', '.x64', '.t64', '.tap', '.prg', '.p00', '.lnx'}
        
        disk_files = []
        
        # Recursively find all disk files
        for file in folder.rglob('*'):
            if file.is_file() and file.suffix.lower() in disk_extensions:
                disk_files.append(file)
        
        # Sort files to ensure consistent ordering
        disk_files.sort()
        
        # Rename disk files
        for index, file in enumerate(disk_files, start=1):
            ext = file.suffix.lower()
            new_name = f"{game_name}_d{index}{ext}"
            new_path = file.parent / new_name
            
            if new_path != file:
                file.rename(new_path)
    
    def build_destination_path(self, template: str, metadata: Dict[str, str | None], 
                               zip_path: Path, root: Path) -> Path:
        """
        Build destination path from template and metadata.
        
        Template can use placeholders like:
        {name}, {primary_genre}, {secondary_genre}, {language}, {published_year}, 
        {publisher}, {players}, {control}, {pal_ntsc}, {developer}, {coding}, 
        {graphics}, {music}, {comment}, {unique_id}
        
        Example: "{primary_genre}/{secondary_genre}/{language}/{name}"
        
        Args:
            template: Path template with placeholders
            metadata: Parsed metadata dictionary
            zip_path: Original zip file path
            root: Root destination directory
            
        Returns:
            Full Path object for the destination
        """
        # Build substitution dict with all metadata fields, sanitized
        subs = {
            'name': self.sanitize_folder_name(metadata.get('name') or zip_path.stem),
            'primary_genre': self.sanitize_folder_name(metadata.get('primary_genre') or 'Unknown'),
            'secondary_genre': self.sanitize_folder_name(metadata.get('secondary_genre') or 'Other'),
            'language': self.sanitize_folder_name(metadata.get('language') or 'Unknown'),
            'published_year': (metadata.get('published_year') or 'Unknown').replace('?', 'x'),
            'publisher': self.sanitize_folder_name(metadata.get('publisher') or 'Unknown'),
            'players': self.sanitize_folder_name(metadata.get('players') or 'Unknown'),
            'control': self.sanitize_folder_name(metadata.get('control') or 'Unknown'),
            'pal_ntsc': self.sanitize_folder_name(metadata.get('pal_ntsc') or 'Unknown'),
            'developer': self.sanitize_folder_name(metadata.get('developer') or 'Unknown'),
            'coding': self.sanitize_folder_name(metadata.get('coding') or 'Unknown'),
            'graphics': self.sanitize_folder_name(metadata.get('graphics') or 'Unknown'),
            'music': self.sanitize_folder_name(metadata.get('music') or 'Unknown'),
            'comment': self.sanitize_folder_name(metadata.get('comment') or 'Unknown'),
            'unique_id': metadata.get('unique_id') or 'Unknown',
        }
        
        # Validate template and provide helpful error message
        try:
            path_str = template.format(**subs)
        except KeyError as e:
            invalid_field = str(e).strip("'")
            valid_fields = ', '.join(sorted(subs.keys()))
            raise ValueError(
                f"Invalid template field: {{{invalid_field}}}\n"
                f"Valid fields are: {valid_fields}\n"
                f"Check your template for typos!"
            ) from e
        
        # Build full path
        return root / path_str
    
    def sanitize_folder_name(self, name: str) -> str:
        """
        Remove invalid Windows filename characters.
        
        Args:
            name: Folder name to sanitize
            
        Returns:
            Sanitized folder name
        """
        # Replace backslash and forward slash with dash (to prevent path injection)
        sanitized = re.sub(r'[\\/]', '-', name)
        
        # Remove square brackets (common in publisher names)
        sanitized = re.sub(r'[\[\]]', '', sanitized)
        
        # Remove other invalid Windows characters
        invalid_chars = r'[<>:"|?*]'
        sanitized = re.sub(invalid_chars, '', sanitized)
        
        # Strip leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')
        
        return sanitized
    
    def organize_games(self, move_files: bool = False, folder_template: str = "{primary_genre}/{secondary_genre}/{language}/{name}", english_only: bool = False, include_no_text: bool = False, collapse_publishers: bool = False, keep_zipped: bool = False) -> None:
        """
        Scan source directory and organize games into destination structure.
        
        Processes zipped game archives containing VERSION.NFO files.
        
        Args:
            move_files: If True, move files. If False, copy files (safer for testing)
            folder_template: Template for folder structure using placeholders like {name}, {primary_genre}, etc.
            english_only: If True, only process games with 'English' in language field (case-insensitive)
            include_no_text: If True, include games with '(No Text)' when english_only is True
            collapse_publishers: If True, remove everything after ' - ' in publisher names
            keep_zipped: If True, copy/move the zip file instead of extracting contents
        """
        if not self.source_root.exists():
            print(f"Error: Source directory '{self.source_root}' does not exist")
            return
        
        # Create destination directory if it doesn't exist
        self.destination_root.mkdir(parents=True, exist_ok=True)
        
        # Open log file
        log_file_path = self.destination_root / "organization_log.txt"
        log_file = open(log_file_path, 'w', encoding='utf-8')
        
        print(f"Scanning: {self.source_root}")
        log_file.write(f"Scanning: {self.source_root}\n")
        print(f"Destination: {self.destination_root}")
        log_file.write(f"Destination: {self.destination_root}\n")
        print("-" * 60)
        log_file.write("-" * 60 + "\n")
        
        # Process ZIP files only
        zip_count = 0
        
        for zip_file in self.source_root.rglob('*.zip'):
            zip_count += 1
            self.games_found += 1
            self._process_zip_file(zip_file, move_files, folder_template, english_only, include_no_text, collapse_publishers, keep_zipped)
        
        # Print summary
        print("-" * 60)
        log_file.write("-" * 60 + "\n")
        
        summary_lines = [
            "Summary:",
            f"  Games found: {self.games_found}",
            f"  Games organized: {self.games_moved}",
        ]
        
        if self.errors:
            summary_lines.append(f"  Errors/Duplicates: {len(self.errors)}")
            summary_lines.append("  Details:")
            for error in self.errors:
                summary_lines.append(f"    - {error}")
        
        for line in summary_lines:
            print(line)
            log_file.write(line + "\n")
        
        log_file.close()
        print(f"\nLog file saved to: {log_file_path}")
    
    def _process_zip_file(self, zip_path: Path, move_files: bool, folder_template: str, english_only: bool = False, include_no_text: bool = False, collapse_publishers: bool = False, keep_zipped: bool = False) -> None:
        """
        Process a zipped game file.
        
        Extracts, parses metadata, renames disk files, and organizes to destination.
        
        Args:
            zip_path: Path to zip file
            move_files: Whether to move or copy files
            folder_template: Template for destination folder structure
            english_only: If True, skip games without 'English' in language field (case-insensitive)
            include_no_text: If True, include games with '(No Text)' when english_only is True
            collapse_publishers: If True, remove everything after ' - ' in publisher names
            keep_zipped: If True, copy/move the zip file instead of extracting contents
        """
        # Extract zip to temporary location
        temp_dir = self.extract_zip_to_temp(zip_path)
        if temp_dir is None:
            print(f"✗ ERROR: {zip_path.name} - Could not extract zip")
            return
        
        try:
            # Find VERSION.NFO in extracted files
            nfo_file = self.find_version_nfo(temp_dir)
            if nfo_file is None:
                print(f"✗ SKIP: {zip_path.stem} - No VERSION.NFO found in archive")
                self.errors.append(f"No VERSION.NFO in {zip_path.name}")
                return
            
            # Parse metadata
            metadata = self.parse_version_nfo(nfo_file)
            if metadata is None:
                print(f"⚠ SKIP: {zip_path.stem} - Could not parse VERSION.NFO")
                self.errors.append(f"Could not parse metadata for {zip_path.name}")
                return
            
            # Collapse publisher name if requested (remove everything after / or \)
            if collapse_publishers and metadata.get('publisher'):
                publisher = metadata['publisher']
                if publisher:  # Ensure publisher is not None
                    # Only check for / and \ (separators in publisher names)
                    for separator in ['/', '\\']:
                        if separator in publisher:
                            metadata['publisher'] = publisher.split(separator)[0].strip()
                            break
            
            # Check English-only filter
            if english_only:
                language = metadata.get('language') or ''
                # Case-insensitive check for English
                has_english = 'english' in language.lower()
                is_no_text = '(no text)' in language.lower()
                
                # Skip if not English (unless it's (No Text) and that's allowed)
                if not has_english and not (include_no_text and is_no_text):
                    print(f"⚠ SKIP: {zip_path.stem} - Not English (Language: {language})")
                    return
            
            # Get game name for destination
            game_name = self.sanitize_folder_name(metadata.get('name') or zip_path.stem)
            
            # Create destination path using template
            dest_path = self.build_destination_path(folder_template, metadata, zip_path, self.destination_root)

            if keep_zipped:
                # Copy/move the zip file without extracting
                # Always include game name in the zip filename
                final_dest = dest_path / f"{game_name}.zip"

                # Check if destination already exists - if so, add version number
                version = 2
                while final_dest.exists():
                    versioned_name = f"{game_name} [v{version}].zip"
                    final_dest = dest_path / versioned_name
                    version += 1

                # Create destination directory and copy/move the zip file
                final_dest.parent.mkdir(parents=True, exist_ok=True)

                if move_files:
                    shutil.move(str(zip_path), str(final_dest))
                    operation = "MOVED"
                else:
                    shutil.copy2(str(zip_path), str(final_dest))
                    operation = "COPIED"

                self.games_moved += 1
                print(f"✓ {operation}: {zip_path.name}")
                print(f"  → {final_dest.relative_to(self.destination_root)}")
            else:
                # Extract and organize (original behavior)
                game_folder = nfo_file.parent

                # Rename disk files in the game folder
                self.rename_disk_files(game_folder, game_name)

                # Determine if template ends with {name} (or equivalent)
                # If so, do NOT add extra game_name subfolder
                template_stripped = folder_template.strip().replace(' ', '')
                ends_with_name = template_stripped.endswith('{name}')

                if ends_with_name:
                    final_dest = dest_path
                else:
                    final_dest = dest_path / game_name

                # Check if destination already exists - if so, add version number
                version = 2
                while final_dest.exists():
                    if ends_with_name:
                        versioned_name = f"{game_name} [v{version}]"
                        final_dest = dest_path.parent / versioned_name
                    else:
                        versioned_name = f"{game_name} [v{version}]"
                        final_dest = dest_path / versioned_name
                    version += 1

                # Create destination directory and copy the game folder
                final_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(game_folder, final_dest)

                self.games_moved += 1
                print(f"✓ EXTRACTED: {zip_path.name}")
                print(f"  → {final_dest.relative_to(self.destination_root)}")
        
        finally:
            # Clean up temporary directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


def main():
    """
    Main entry point for the Gamebase Game Organizer.
    
    Supports both command-line arguments and interactive prompts.
    """
    parser = argparse.ArgumentParser(
        description='GameBase64 Game Organizer - Organize games from zipped archives',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gb64_reorganizer.py
    (Interactive mode - prompts for all options)
  
  python gb64_reorganizer.py "S:\\Source" "S:\\Dest"
    (Organize with default settings)
  
  python gb64_reorganizer.py "S:\\Source" "S:\\Dest" --template "{publisher}/{name}" --english-only --collapse-publishers
    (Organize with custom options)
        """
    )
    
    parser.add_argument('source', nargs='?', help='Source directory containing zipped games')
    parser.add_argument('destination', nargs='?', help='Destination directory for organized games')
    parser.add_argument('--template', default='{primary_genre}/{secondary_genre}/{language}/{name}',
                       help='Folder structure template (default: {primary_genre}/{secondary_genre}/{language}/{name})')
    parser.add_argument('--english-only', action='store_true',
                       help='Only process games with English language')
    parser.add_argument('--include-no-text', action='store_true',
                       help='Include (No Text) games when using --english-only')
    parser.add_argument('--collapse-publishers', action='store_true',
                       help='Remove text after dash in publisher names')
    parser.add_argument('--keep-zipped', action='store_true',
                       help='Copy/move zip files without extracting')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("GAMEBASE64 GAME ORGANIZER v1.3.0")
    print("=" * 60)
    
    # Get directories - from args or interactive prompts
    if args.source and args.destination:
        source = args.source
        destination = args.destination
        template = args.template
        english_only = args.english_only
        include_no_text = args.include_no_text
        collapse_publishers = args.collapse_publishers
        keep_zipped = args.keep_zipped
        
        print(f"\nSource: {source}")
        print(f"Destination: {destination}")
        print(f"Template: {template}")
        if english_only:
            print(f"English filter: {'English + (No Text)' if include_no_text else 'English only'}")
        if collapse_publishers:
            print("Publisher collapse: Enabled")
        if keep_zipped:
            print("Keep zipped: Yes (files will not be extracted)")
    else:
        # Interactive mode
        source = input("\nEnter source directory (zipped games): ").strip()
        destination = input("Enter destination directory (organized output): ").strip()
        
        if not source or not destination:
            print("Error: Both directories are required.")
            return
        
        # Get folder template (optional)
        print("\nFolder Template (press Enter for default):")
        print("Available fields: {name}, {primary_genre}, {secondary_genre}, {language},")
        print("                  {published_year}, {publisher}, {developer}, {players},")
        print("                  {control}, {pal_ntsc}, {unique_id}, {coding}, {graphics},")
        print("                  {music}, {comment}")
        print("\nDefault: {primary_genre}/{secondary_genre}/{language}/{name}")
        print("Examples:")
        print("  - {published_year}/{primary_genre}/{name}")
        print("  - {publisher}/{name}")
        print("  - {primary_genre}/{language}/{name}")
        
        template = input("\nTemplate: ").strip()
        if not template:
            template = "{primary_genre}/{secondary_genre}/{language}/{name}"
            print(f"Using default template: {template}")
        
        # Ask about English-only filter
        english_filter = input("\nOnly process games with English language? (y/n): ").strip().lower()
        english_only = english_filter == 'y'
        
        include_no_text = False
        if english_only:
            no_text_filter = input("Include games with '(No Text)' language? (y/n): ").strip().lower()
            include_no_text = no_text_filter == 'y'
            
            if include_no_text:
                print("Filtering: Only games with 'English' or '(No Text)' in language field will be processed")
            else:
                print("Filtering: Only games with 'English' in language field will be processed")
        
        # Ask about publisher collapsing
        collapse_filter = input("\nCollapse publisher names (remove text after ' - ')? (y/n): ").strip().lower()
        collapse_publishers = collapse_filter == 'y'
        
        if collapse_publishers:
            print("Publisher names will be collapsed (e.g., 'Activision - Games' → 'Activision')")
        
        # Ask about keeping files zipped
        keep_zip = input("\nKeep files zipped (do not extract)? (y/n): ").strip().lower()
        keep_zipped = keep_zip == 'y'
        
        if keep_zipped:
            print("Files will remain zipped (no extraction)")
    
    # Create organizer and process games
    organizer = GamebaseOrganizer(source, destination)
    organizer.organize_games(move_files=False, folder_template=template, english_only=english_only, include_no_text=include_no_text, collapse_publishers=collapse_publishers, keep_zipped=keep_zipped)


if __name__ == "__main__":
    main()
