#!/usr/bin/env python3
"""
C64 Game Organizer

A utility to organize Commodore 64 games from zipped archives into a
structured folder hierarchy based on Genre, SubGenre, and Language metadata
extracted from VERSION.NFO files.

Author: Jason Carr
Date: January 2026
"""

from pathlib import Path
import shutil
import zipfile
import tempfile
import re
from typing import Optional, Dict


class C64GameOrganizer:
    """
    Organizes Commodore 64 games from zip archives into a structured folder hierarchy.
    
    Extracts games from zip files, parses VERSION.NFO metadata, and creates a folder
    structure: Destination/PrimaryGenre/SecondaryGenre/Language/GameName/
    
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
            source_dir: Directory containing zip files of C64 games
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
    
    def parse_version_nfo(self, nfo_path: Path) -> Optional[Dict[str, str]]:
        """
        Parse VERSION.NFO file and extract game metadata.
        
        Extracts: Name, Genre (primary/secondary), Language
        Genre format: "Primary - Secondary" (splits on dash)
        
        Args:
            nfo_path: Path to VERSION.NFO file
            
        Returns:
            Dictionary with keys: 'name', 'primary_genre', 'secondary_genre', 'language'
            Returns None if parsing fails
        """
        try:
            with open(nfo_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
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
            
            return {
                'name': name,
                'primary_genre': primary_genre,
                'secondary_genre': secondary_genre,
                'language': language
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
    
    def sanitize_folder_name(self, name: str) -> str:
        """
        Remove invalid Windows filename characters.
        
        Args:
            name: Folder name to sanitize
            
        Returns:
            Sanitized folder name
        """
        # Remove invalid Windows characters
        invalid_chars = r'[<>:"|?*]'
        sanitized = re.sub(invalid_chars, '', name)
        
        # Strip leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')
        
        return sanitized
    
    def organize_games(self, move_files: bool = False) -> None:
        """
        Scan source directory and organize games into destination structure.
        
        Processes zipped game archives containing VERSION.NFO files.
        
        Args:
            move_files: If True, move files. If False, copy files (safer for testing)
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
            self._process_zip_file(zip_file, move_files)
        
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
    
    def _process_zip_file(self, zip_path: Path, move_files: bool) -> None:
        """
        Process a zipped game file.
        
        Extracts, parses metadata, renames disk files, and organizes to destination.
        
        Args:
            zip_path: Path to zip file
            move_files: Whether to move or copy files
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
            
            # Get game name from NFO and sanitize folder names
            game_name = self.sanitize_folder_name(metadata.get('name', zip_path.stem))
            primary_genre = self.sanitize_folder_name(metadata['primary_genre'])
            secondary_genre = self.sanitize_folder_name(metadata['secondary_genre'])
            language = self.sanitize_folder_name(metadata['language'])
            
            # Get the actual game folder (parent of VERSION.NFO)
            game_folder = nfo_file.parent
            
            # Rename disk files in the game folder
            self.rename_disk_files(game_folder, game_name)
            
            # Create destination path
            dest_path = self.destination_root / primary_genre / secondary_genre / language / game_name
            
            # Check if destination already exists - if so, add version number
            version = 2
            original_dest = dest_path
            while dest_path.exists():
                versioned_name = f"{game_name} [v{version}]"
                dest_path = self.destination_root / primary_genre / secondary_genre / language / versioned_name
                version += 1
            
            # Create destination directory and copy the game folder
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(game_folder, dest_path)
            
            self.games_moved += 1
            print(f"✓ EXTRACTED: {zip_path.name}")
            print(f"  → {primary_genre} / {secondary_genre} / {language} / {game_name}")
        
        finally:
            # Clean up temporary directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


def main():
    """
    Main entry point for the C64 Game Organizer.
    
    Prompts user for source and destination directories,
    then organizes all C64 games in those directories.
    """
    print("\n" + "=" * 60)
    print("C64 GAME ORGANIZER")
    print("=" * 60)
    
    # Get directories from user
    source = input("\nEnter source directory (zipped games): ").strip()
    destination = input("Enter destination directory (organized output): ").strip()
    
    if not source or not destination:
        print("Error: Both directories are required.")
        return
    
    # Create organizer and process games
    organizer = C64GameOrganizer(source, destination)
    organizer.organize_games(move_files=False)


if __name__ == "__main__":
    main()
