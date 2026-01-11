#!/usr/bin/env python3
"""
Gamebase Game Organizer - GUI Edition

Compact, efficient GUI for organizing games from zipped archives.

Author: Jason Carr
Date: January 2026
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font
import threading
import queue
import sys
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict

from gb64_reorganizer import GamebaseOrganizer


@dataclass
class GameInfo:
    """Container for discovered game information."""
    zip_name: str
    zip_path: str  # Changed from Path to str for JSON serialization
    modification_time: float = 0.0  # File modification timestamp
    name: Optional[str] = None
    primary_genre: Optional[str] = None
    secondary_genre: Optional[str] = None
    language: Optional[str] = None
    published_year: Optional[str] = None
    publisher: Optional[str] = None
    players: Optional[str] = None
    control: Optional[str] = None
    pal_ntsc: Optional[str] = None
    unique_id: Optional[str] = None
    developer: Optional[str] = None
    coding: Optional[str] = None
    graphics: Optional[str] = None
    music: Optional[str] = None
    comment: Optional[str] = None
    selected: bool = False
    error: Optional[str] = None
    
    def to_path(self):
        """Convert zip_path string back to Path object."""
        return Path(self.zip_path)


class GamebaseGameScannerThread(threading.Thread):
    """Background thread for scanning game archives."""
    
    def __init__(self, source_dir: Path, output_queue: queue.Queue, use_cache: bool = True):
        super().__init__(daemon=True)
        self.source_dir = source_dir
        self.output_queue = output_queue
        self.use_cache = use_cache
        self.stop_flag = threading.Event()
        self.cache_file = source_dir / '.gamebase_cache.json'
    
    def run(self):
        """Scan directory and parse game metadata."""
        try:
            organizer = GamebaseOrganizer(str(self.source_dir), "")
            
            # Load cache if enabled
            cache = {}
            if self.use_cache and self.cache_file.exists():
                try:
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                        cache = {item['zip_name']: item for item in cache_data}
                    self.output_queue.put(('log', f"Loaded cache with {len(cache)} entries"))
                except Exception as e:
                    self.output_queue.put(('log', f"Cache load failed: {e}"))
            
            # Count total files first for progress tracking
            all_zips = sorted(self.source_dir.rglob('*.zip'))
            total_count = len(all_zips)
            self.output_queue.put(('total', total_count))
            
            # Determine which files need scanning
            files_to_scan = []
            cached_count = 0
            
            for zip_file in all_zips:
                mod_time = zip_file.stat().st_mtime
                cached_entry = cache.get(zip_file.name)
                
                if cached_entry and cached_entry.get('modification_time') == mod_time:
                    # Use cached data
                    game_info = GameInfo(**cached_entry)
                    self.output_queue.put(('game', game_info))
                    cached_count += 1
                else:
                    # Need to scan
                    files_to_scan.append((zip_file, mod_time))
            
            if cached_count > 0:
                self.output_queue.put(('log', f"Using {cached_count} cached entries, scanning {len(files_to_scan)} new/changed files"))
            
            # Scan new/changed files
            for index, (zip_file, mod_time) in enumerate(files_to_scan, start=1):
                # Check for cancellation
                if self.stop_flag.is_set():
                    self.output_queue.put(('cancelled', None))
                    return
                
                # Send progress update
                current = cached_count + index
                self.output_queue.put(('progress', current, total_count))
                
                game_info = GameInfo(
                    zip_name=zip_file.name, 
                    zip_path=str(zip_file),
                    modification_time=mod_time
                )
                
                temp_dir = organizer.extract_zip_to_temp(zip_file)
                if temp_dir:
                    try:
                        nfo_file = organizer.find_version_nfo(Path(temp_dir))
                        if nfo_file:
                            metadata = organizer.parse_version_nfo(nfo_file)
                            if metadata:
                                game_info.name = metadata.get('name', zip_file.stem)
                                game_info.primary_genre = metadata.get('primary_genre', 'Unknown')
                                game_info.secondary_genre = metadata.get('secondary_genre', 'Other')
                                game_info.language = metadata.get('language', 'Unknown')
                                game_info.published_year = metadata.get('published_year', 'Unknown')
                                game_info.publisher = metadata.get('publisher', 'Unknown')
                                game_info.players = metadata.get('players', 'Unknown')
                                game_info.control = metadata.get('control', 'Unknown')
                                game_info.pal_ntsc = metadata.get('pal_ntsc', 'Unknown')
                                game_info.unique_id = metadata.get('unique_id')
                                game_info.developer = metadata.get('developer')
                                game_info.coding = metadata.get('coding')
                                game_info.graphics = metadata.get('graphics')
                                game_info.music = metadata.get('music')
                                game_info.comment = metadata.get('comment')
                            else:
                                game_info.error = "No metadata"
                        else:
                            game_info.error = "No VERSION.NFO"
                        
                        import shutil
                        if Path(temp_dir).exists():
                            shutil.rmtree(temp_dir)
                    except Exception as e:
                        game_info.error = str(e)
                else:
                    game_info.error = "Extract failed"
                
                self.output_queue.put(('game', game_info))
            
            # Save cache if enabled
            if self.use_cache:
                try:
                    all_games = []
                    # Collect all games from queue (cached + newly scanned)
                    # Note: We'll need to save this from the GUI after collection
                    self.output_queue.put(('save_cache', self.cache_file))
                except Exception as e:
                    self.output_queue.put(('log', f"Cache save failed: {e}"))
            
            self.output_queue.put(('done', None))
        except Exception as e:
            self.output_queue.put(('error', str(e)))
            self.output_queue.put(('done', None))


class GamebaseOrganizationThread(threading.Thread):
    """Background thread for organizing games."""
    
    def __init__(self, games: List[GameInfo], destination_dir: Path, 
                 folder_template: str, move_files: bool, keep_zipped: bool, 
                 output_queue: queue.Queue):
        super().__init__(daemon=True)
        self.games = games
        self.destination_dir = destination_dir
        self.folder_template = folder_template
        self.move_files = move_files
        self.keep_zipped = keep_zipped
        self.output_queue = output_queue
        self.stop_flag = threading.Event()
    
    def run(self):
        """Organize selected games."""
        selected_games = [g for g in self.games if g.selected]
        total = len(selected_games)
        
        for index, game in enumerate(selected_games, start=1):
            # Check for cancellation
            if self.stop_flag.is_set():
                self.output_queue.put(('cancelled', None))
                return
            
            # Send progress update
            self.output_queue.put(('progress', index, total))
            
            temp_dir = None
            try:
                organizer = GamebaseOrganizer(str(self.destination_dir.parent), str(self.destination_dir))
                temp_dir = organizer.extract_zip_to_temp(game.to_path())
                
                if not temp_dir:
                    self.output_queue.put(('log', f"✗ Failed to extract: {game.zip_name}"))
                    continue
                
                nfo_file = organizer.find_version_nfo(Path(temp_dir))
                if not nfo_file:
                    self.output_queue.put(('log', f"✗ No VERSION.NFO in: {game.zip_name}"))
                    continue
                
                metadata = organizer.parse_version_nfo(nfo_file)
                if not metadata:
                    self.output_queue.put(('log', f"✗ Parse failed: {game.zip_name}"))
                    continue
                
                # Build destination path using template
                dest_path = organizer.build_destination_path(
                    self.folder_template, 
                    metadata, 
                    game.to_path(), 
                    self.destination_dir
                )
                
                game_folder = Path(temp_dir)
                contents = list(game_folder.iterdir())
                if len(contents) == 1 and contents[0].is_dir():
                    game_folder = contents[0]
                
                game_name = organizer.sanitize_folder_name(metadata.get('name') or game.to_path().stem)
                organizer.rename_disk_files(game_folder, game_name)
                
                # Add game name as an additional subfolder to store the game files
                final_game_path = dest_path / game_name
                
                # Handle duplicates
                version = 2
                while final_game_path.exists():
                    versioned_name = f"{game_name} [v{version}]"
                    final_game_path = dest_path / versioned_name
                    version += 1
                
                final_game_path.parent.mkdir(parents=True, exist_ok=True)
                
                import shutil
                shutil.copytree(game_folder, final_game_path)
                
                self.output_queue.put(('log', f"✓ {game.zip_name}"))
            
            finally:
                if temp_dir and Path(temp_dir).exists():
                    import shutil
                    shutil.rmtree(temp_dir)
        
        self.output_queue.put(('done', None))


class GamebaseGameOrganizerGUI:
    """Main GUI application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gamebase Game Organizer (WIP - Experimental)")
        self.root.geometry("1250x750")
        
        self.source_dir = None
        self.destination_dir = None
        self.games: List[GameInfo] = []
        self.output_queue = queue.Queue()
        self.scanner_thread = None
        self.organizer_thread = None
        
        # Filter variables (initialized in _create_widgets)
        self.genre_filter = tk.StringVar(value="")
        self.subgenre_filter = tk.StringVar(value="")
        self.language_filter = tk.StringVar(value="")
        self.year_filter = tk.StringVar(value="")
        self.publisher_filter = tk.StringVar(value="")
        self.players_filter = tk.StringVar(value="")
        self.control_filter = tk.StringVar(value="")
        self.pal_ntsc_filter = tk.StringVar(value="")
        
        # Comboboxes (initialized in _create_widgets)
        self.genre_combo: ttk.Combobox = None  # type: ignore
        self.subgenre_combo: ttk.Combobox = None  # type: ignore
        self.language_combo: ttk.Combobox = None  # type: ignore
        self.year_combo: ttk.Combobox = None  # type: ignore
        self.publisher_combo: ttk.Combobox = None  # type: ignore
        self.players_combo: ttk.Combobox = None  # type: ignore
        self.control_combo: ttk.Combobox = None  # type: ignore
        self.pal_ntsc_combo: ttk.Combobox = None  # type: ignore
        
        self._create_widgets()
        self._check_queue()
    
    def _create_widgets(self):
        """Create GUI widgets."""
        main = ttk.Frame(self.root, padding="6")
        main.pack(fill=tk.BOTH, expand=True)
        
        # TOP: Folder selection
        top = ttk.Frame(main)
        top.pack(fill=tk.X, pady=(0, 6))
        
        ttk.Label(top, text="Source:").pack(side=tk.LEFT, padx=2)
        self.source_label = ttk.Label(top, text="Select folder...", foreground="gray", width=30)
        self.source_label.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(top, text="Browse", command=self._browse_source, width=9).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(top, text="Dest:").pack(side=tk.LEFT, padx=2)
        self.dest_label = ttk.Label(top, text="Select folder...", foreground="gray", width=30)
        self.dest_label.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(top, text="Browse", command=self._browse_destination, width=9).pack(side=tk.LEFT, padx=2)
        
        # MIDDLE: Horizontal split - Filters on left, Games on right
        middle = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        middle.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        
        # LEFT: Filters (compact)
        filters = ttk.LabelFrame(middle, text="Filters", padding="4")
        middle.add(filters, weight=0)
        
        # Genre
        f = ttk.Frame(filters)
        f.pack(fill=tk.X, pady=1)
        ttk.Label(f, text="Genre", width=10).pack(side=tk.LEFT, padx=1)
        self.genre_combo = ttk.Combobox(f, textvariable=self.genre_filter, state="readonly", width=18)
        self.genre_combo.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        self.genre_combo.bind("<<ComboboxSelected>>", lambda e: [self._update_filters(), self._apply_filters()])
        
        # Sub-Genre
        f = ttk.Frame(filters)
        f.pack(fill=tk.X, pady=1)
        ttk.Label(f, text="Sub-Genre", width=10).pack(side=tk.LEFT, padx=1)
        self.subgenre_combo = ttk.Combobox(f, textvariable=self.subgenre_filter, state="readonly", width=18)
        self.subgenre_combo.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        self.subgenre_combo.bind("<<ComboboxSelected>>", lambda e: [self._update_filters(), self._apply_filters()])
        
        # Language
        f = ttk.Frame(filters)
        f.pack(fill=tk.X, pady=1)
        ttk.Label(f, text="Language", width=10).pack(side=tk.LEFT, padx=1)
        self.language_combo = ttk.Combobox(f, textvariable=self.language_filter, state="readonly", width=18)
        self.language_combo.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        self.language_combo.bind("<<ComboboxSelected>>", lambda e: [self._update_filters(), self._apply_filters()])
        
        # Year
        f = ttk.Frame(filters)
        f.pack(fill=tk.X, pady=1)
        ttk.Label(f, text="Year", width=10).pack(side=tk.LEFT, padx=1)
        self.year_combo = ttk.Combobox(f, textvariable=self.year_filter, state="readonly", width=18)
        self.year_combo.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        self.year_combo.bind("<<ComboboxSelected>>", lambda e: [self._update_filters(), self._apply_filters()])
        
        # Publisher
        f = ttk.Frame(filters)
        f.pack(fill=tk.X, pady=1)
        ttk.Label(f, text="Publisher", width=10).pack(side=tk.LEFT, padx=1)
        self.publisher_combo = ttk.Combobox(f, textvariable=self.publisher_filter, state="readonly", width=18)
        self.publisher_combo.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        self.publisher_combo.bind("<<ComboboxSelected>>", lambda e: [self._update_filters(), self._apply_filters()])
        
        # Players
        f = ttk.Frame(filters)
        f.pack(fill=tk.X, pady=1)
        ttk.Label(f, text="Players", width=10).pack(side=tk.LEFT, padx=1)
        self.players_combo = ttk.Combobox(f, textvariable=self.players_filter, state="readonly", width=18)
        self.players_combo.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        self.players_combo.bind("<<ComboboxSelected>>", lambda e: [self._update_filters(), self._apply_filters()])
        
        # Control
        f = ttk.Frame(filters)
        f.pack(fill=tk.X, pady=1)
        ttk.Label(f, text="Control", width=10).pack(side=tk.LEFT, padx=1)
        self.control_combo = ttk.Combobox(f, textvariable=self.control_filter, state="readonly", width=18)
        self.control_combo.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        self.control_combo.bind("<<ComboboxSelected>>", lambda e: [self._update_filters(), self._apply_filters()])
        
        # Pal/NTSC
        f = ttk.Frame(filters)
        f.pack(fill=tk.X, pady=1)
        ttk.Label(f, text="Pal/NTSC", width=10).pack(side=tk.LEFT, padx=1)
        self.pal_ntsc_combo = ttk.Combobox(f, textvariable=self.pal_ntsc_filter, state="readonly", width=18)
        self.pal_ntsc_combo.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        self.pal_ntsc_combo.bind("<<ComboboxSelected>>", lambda e: [self._update_filters(), self._apply_filters()])
        
        ttk.Button(filters, text="Clear", command=self._clear_filters).pack(fill=tk.X, pady=4)
        
        # Details panel in left pane
        details_frame = ttk.LabelFrame(filters, text="Details", padding="2")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        
        # Use a font with better Unicode support (Segoe UI, Consolas, or fallback to system default)
        details_font = ("Segoe UI", 9) if "Segoe UI" in font.families() else ("Courier", 9)
        self.details_text = scrolledtext.ScrolledText(details_frame, height=8, wrap=tk.WORD, state=tk.DISABLED, font=details_font)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        # RIGHT: Game list
        games_frame = ttk.LabelFrame(middle, text="Games", padding="2")
        middle.add(games_frame, weight=1)
        
        sb = ttk.Scrollbar(games_frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.game_tree = ttk.Treeview(
            games_frame,
            columns=("name", "genre", "subgenre", "year", "players", "control", "status"),
            show="headings",
            yscrollcommand=sb.set,
            height=20
        )
        sb.config(command=self.game_tree.yview)
        
        self.game_tree.column("name", width=180, anchor=tk.W)
        self.game_tree.column("genre", width=100, anchor=tk.W)
        self.game_tree.column("subgenre", width=100, anchor=tk.W)
        self.game_tree.column("year", width=45, anchor=tk.W)
        self.game_tree.column("players", width=70, anchor=tk.W)
        self.game_tree.column("control", width=85, anchor=tk.W)
        self.game_tree.column("status", width=80, anchor=tk.W)
        
        for col in ["name", "genre", "subgenre", "year", "players", "control", "status"]:
            self.game_tree.heading(col, text=col.title())
        
        self.game_tree.pack(fill=tk.BOTH, expand=True)
        self.game_tree.bind("<Button-1>", self._on_game_click)
        self.game_tree.bind("<Button-3>", self._show_game_context_menu)
        
        # BOTTOM: Options
        bottom = ttk.Frame(main)
        bottom.pack(fill=tk.X, pady=(0, 6))
        
        ttk.Label(bottom, text="Template:").pack(side=tk.LEFT, padx=2)
        self.template_var = tk.StringVar(value="{primary_genre}/{secondary_genre}/{language}/{name}")
        template_entry = ttk.Entry(
            bottom,
            textvariable=self.template_var,
            width=40
        )
        template_entry.pack(side=tk.LEFT, padx=2)
        
        # Helper button to show available placeholders
        ttk.Button(
            bottom,
            text="?",
            command=self._show_template_help,
            width=2
        ).pack(side=tk.LEFT, padx=1)
        
        ttk.Label(bottom, text="Op:").pack(side=tk.LEFT, padx=8)
        self.operation_var = tk.StringVar(value="copy")
        ttk.Radiobutton(bottom, text="Copy", variable=self.operation_var, value="copy").pack(side=tk.LEFT, padx=1)
        ttk.Radiobutton(bottom, text="Move", variable=self.operation_var, value="move").pack(side=tk.LEFT, padx=1)
        
        self.keep_zipped_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bottom, text="Zipped", variable=self.keep_zipped_var).pack(side=tk.LEFT, padx=8)
        
        ttk.Button(bottom, text="Scan", command=self._scan_source, width=8).pack(side=tk.LEFT, padx=2)
        self.cancel_button = ttk.Button(bottom, text="Cancel", command=self._cancel_operation, width=8, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom, text="Select All", command=self._select_all_games, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom, text="Deselect All", command=self._deselect_all_games, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom, text="Organize", command=self._organize_games, width=10).pack(side=tk.LEFT, padx=2)
        
        # LOG
        log_frame = ttk.LabelFrame(main, text="Log", padding="2")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.progress = ttk.Progressbar(log_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 2))
        
        self.progress_label = ttk.Label(log_frame, text="Ready", font=("TkDefaultFont", 8))
        self.progress_label.pack(fill=tk.X)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=4, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _browse_source(self):
        """Browse for source directory."""
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_dir = Path(folder)
            self.source_label.config(text=str(self.source_dir), foreground="black")
    
    def _browse_destination(self):
        """Browse for destination directory."""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.destination_dir = Path(folder)
            self.dest_label.config(text=str(self.destination_dir), foreground="black")
    
    def _scan_source(self):
        """Scan source directory for games."""
        if not self.source_dir:
            messagebox.showwarning("Warning", "Select source folder first")
            return
        
        self.games.clear()
        for item in self.game_tree.get_children():
            self.game_tree.delete(item)
        self.log_text.delete(1.0, tk.END)
        self.progress['value'] = 0
        
        self._log_message("Scanning...")
        self.progress_label.config(text="Scanning...")
        
        self.scanner_thread = GamebaseGameScannerThread(self.source_dir, self.output_queue)
        self.scanner_thread.start()
        self.cancel_button.config(state=tk.NORMAL)
    
    def _check_queue(self):
        """Check for messages from background threads."""
        update_ui = False
        batch_count = 0
        
        try:
            while True:
                msg_type, data = self.output_queue.get_nowait()
                
                if msg_type == 'total':
                    self._log_message(f"Found {data} zip files to scan...")
                
                elif msg_type == 'game':
                    self.games.append(data)
                    batch_count += 1
                    # Update UI every 10 games to avoid slowdown
                    if batch_count >= 10:
                        update_ui = True
                
                elif msg_type == 'progress':
                    current, total = data
                    progress_pct = int((current / total) * 100)
                    self.progress['value'] = progress_pct
                    self.progress_label.config(text=f"Processing {current}/{total} ({progress_pct}%)")
                
                elif msg_type == 'log':
                    self._log_message(data)
                
                elif msg_type == 'cancelled':
                    self.progress_label.config(text="Cancelled")
                    self._log_message("Operation cancelled by user")
                    self.cancel_button.config(state=tk.DISABLED)
                    update_ui = True
                
                elif msg_type == 'save_cache':
                    cache_file = data
                    self._save_cache(cache_file)
                
                elif msg_type == 'done':
                    self.progress['value'] = 100
                    self.progress_label.config(text=f"Done - {len(self.games)} games found")
                    self.cancel_button.config(state=tk.DISABLED)
                    update_ui = True
                
                elif msg_type == 'error':
                    self._log_message(f"ERROR: {data}")
        
        except queue.Empty:
            pass
        
        # Batch update filters and UI
        if update_ui:
            self._update_filters()
            self._apply_filters()
        
        self.root.after(100, self._check_queue)
    
    def _update_filters(self):
        """Update filter dropdowns based on hierarchical selections."""
        # Filter games based on current selections
        filtered_games = self.games[:]
        
        if self.genre_filter.get():
            filtered_games = [g for g in filtered_games if g.primary_genre == self.genre_filter.get()]
        if self.subgenre_filter.get():
            filtered_games = [g for g in filtered_games if g.secondary_genre == self.subgenre_filter.get()]
        if self.language_filter.get():
            filtered_games = [g for g in filtered_games if g.language == self.language_filter.get()]
        if self.year_filter.get():
            filtered_games = [g for g in filtered_games if g.published_year == self.year_filter.get()]
        if self.publisher_filter.get():
            filtered_games = [g for g in filtered_games if g.publisher == self.publisher_filter.get()]
        if self.players_filter.get():
            filtered_games = [g for g in filtered_games if g.players == self.players_filter.get()]
        if self.control_filter.get():
            filtered_games = [g for g in filtered_games if g.control == self.control_filter.get()]
        if self.pal_ntsc_filter.get():
            filtered_games = [g for g in filtered_games if g.pal_ntsc == self.pal_ntsc_filter.get()]
        
        # Update each filter based on remaining games
        genres = sorted(set(g.primary_genre for g in filtered_games if g.primary_genre))
        self.genre_combo['values'] = [''] + genres
        
        # Sub-genres filtered by selected genre
        if self.genre_filter.get():
            subgenres = sorted(set(g.secondary_genre for g in filtered_games if g.secondary_genre))
        else:
            subgenres = sorted(set(g.secondary_genre for g in self.games if g.secondary_genre))
        self.subgenre_combo['values'] = [''] + subgenres
        
        languages = sorted(set(g.language for g in filtered_games if g.language))
        self.language_combo['values'] = [''] + languages
        
        years = sorted(set(g.published_year for g in filtered_games if g.published_year))
        self.year_combo['values'] = [''] + years
        
        publishers = sorted(set(g.publisher for g in filtered_games if g.publisher))
        self.publisher_combo['values'] = [''] + publishers
        
        players = sorted(set(g.players for g in filtered_games if g.players))
        self.players_combo['values'] = [''] + players
        
        controls = sorted(set(g.control for g in filtered_games if g.control))
        self.control_combo['values'] = [''] + controls
        
        pal_ntscs = sorted(set(g.pal_ntsc for g in filtered_games if g.pal_ntsc))
        self.pal_ntsc_combo['values'] = [''] + pal_ntscs
    
    def _apply_filters(self):
        """Filter and display games."""
        for item in self.game_tree.get_children():
            self.game_tree.delete(item)
        
        for idx, game in enumerate(self.games):
            if self.genre_filter.get() and game.primary_genre != self.genre_filter.get():
                continue
            if self.subgenre_filter.get() and game.secondary_genre != self.subgenre_filter.get():
                continue
            if self.language_filter.get() and game.language != self.language_filter.get():
                continue
            if self.year_filter.get() and game.published_year != self.year_filter.get():
                continue
            if self.publisher_filter.get() and game.publisher != self.publisher_filter.get():
                continue
            if self.players_filter.get() and game.players != self.players_filter.get():
                continue
            if self.control_filter.get() and game.control != self.control_filter.get():
                continue
            if self.pal_ntsc_filter.get() and game.pal_ntsc != self.pal_ntsc_filter.get():
                continue
            
            status = "[✓]" if game.selected else " "
            status += " ✓" if not game.error else f" ✗ {game.error[:15]}"
            
            self.game_tree.insert("", tk.END, iid=f"g{idx}", values=(
                game.name or game.zip_name, 
                game.primary_genre or "?",
                game.secondary_genre or "?",
                game.published_year or "?",
                game.players or "?",
                game.control or "?",
                status
            ))
    
    def _clear_filters(self):
        """Clear all filters."""
        for var in [self.genre_filter, self.subgenre_filter, self.language_filter,
                   self.year_filter, self.publisher_filter, self.players_filter,
                   self.control_filter, self.pal_ntsc_filter]:
            var.set("")
        self._update_filters()
        self._apply_filters()
    
    def _show_game_context_menu(self, event):
        """Show context menu."""
        item = self.game_tree.identify('item', event.x, event.y)
        if not item:
            return
        
        idx = int(item[1:])
        game = self.games[idx]
        
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Toggle Select", command=lambda: self._toggle_select(idx))
        menu.add_command(label="Show in Explorer", command=lambda: self._show_in_explorer(game))
        menu.post(event.x_root, event.y_root)
    
    def _toggle_select(self, idx: int):
        """Toggle game selection."""
        self.games[idx].selected = not self.games[idx].selected
        self._apply_filters()
        self._update_game_details()
    
    def _select_all_games(self):
        """Select all games."""
        for g in self.games:
            g.selected = True
        self._apply_filters()
        self._update_game_details()
    
    def _deselect_all_games(self):
        """Deselect all games."""
        for g in self.games:
            g.selected = False
        self._apply_filters()
        self._update_game_details()
    
    def _update_game_details(self):
        """Display NFO details for selected game (if exactly one selected)."""
        selected = [g for g in self.games if g.selected]
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        
        if len(selected) == 1:
            game = selected[0]
            details = f"""Name: {game.name or 'N/A'}
Zip: {game.zip_name}

Genre: {game.primary_genre or 'N/A'}
Sub-Genre: {game.secondary_genre or 'N/A'}
Language: {game.language or 'N/A'}

Published: {game.published_year or 'N/A'}
Publisher: {game.publisher or 'N/A'}

Players: {game.players or 'N/A'}
Control: {game.control or 'N/A'}
Pal/NTSC: {game.pal_ntsc or 'N/A'}
"""
            if game.error:
                details += f"\nError: {game.error}"
            
            self.details_text.insert('1.0', details)
        elif len(selected) > 1:
            self.details_text.insert('1.0', f"({len(selected)} games selected)")
        else:
            self.details_text.insert('1.0', "(Select one game to view details)")
        
        self.details_text.config(state=tk.DISABLED)
    
    def _on_game_click(self, event):
        """Handle game tree click - show details for highlighted game."""
        item = self.game_tree.identify('item', event.x, event.y)
        if item:
            idx = int(item[1:])
            self._show_game_details(idx)
    
    def _show_game_details(self, idx: int):
        """Display details for a specific game by index."""
        if 0 <= idx < len(self.games):
            game = self.games[idx]
            
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete('1.0', tk.END)
            
            details = f"""Name: {game.name or 'N/A'}
Zip: {game.zip_name}

ID: {game.unique_id or 'N/A'}
Genre: {game.primary_genre or 'N/A'}
Sub-Genre: {game.secondary_genre or 'N/A'}
Language: {game.language or 'N/A'}

Published: {game.published_year or 'N/A'}
Publisher: {game.publisher or 'N/A'}

Developer: {game.developer or 'N/A'}
Coding: {game.coding or 'N/A'}
Graphics: {game.graphics or 'N/A'}
Music: {game.music or 'N/A'}

Players: {game.players or 'N/A'}
Control: {game.control or 'N/A'}
Pal/NTSC: {game.pal_ntsc or 'N/A'}

Comment: {game.comment or 'N/A'}
"""
            if game.error:
                details += f"\nError: {game.error}"
            
            self.details_text.insert('1.0', details)
            self.details_text.config(state=tk.DISABLED)
    
    def _show_template_help(self):
        """Show available template placeholders."""
        help_text = """Available Template Placeholders:

{name}             - Game name
{primary_genre}    - Main game genre
{secondary_genre}  - Sub-genre
{language}         - Language
{published_year}   - Release year
{publisher}        - Publisher name
{developer}        - Developer name
{players}          - Player count
{control}          - Control type
{pal_ntsc}         - Video format
{unique_id}        - GameBase ID
{coding}           - Coding credits
{graphics}         - Graphics credits
{music}            - Music credits
{comment}          - Comments

Example Templates:
  {primary_genre}/{secondary_genre}/{language}/{name}
  {published_year}/{primary_genre}/{name}
  {publisher}/{name}
  {unique_id}/{name}
"""
        messagebox.showinfo("Template Help", help_text)
    
    def _show_in_explorer(self, game: GameInfo):
        """Open Explorer at zip file."""
        try:
            zip_path = game.to_path().resolve()
            if sys.platform == "win32":
                import subprocess
                subprocess.Popen(['explorer', '/select,', str(zip_path)])
            else:
                import subprocess
                subprocess.Popen(['xdg-open', str(zip_path.parent)])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open: {str(e)}")
    
    def _organize_games(self):
        """Organize selected games."""
        if not self.destination_dir:
            messagebox.showwarning("Warning", "Select destination folder first")
            return
        
        selected = [g for g in self.games if g.selected]
        if not selected:
            messagebox.showwarning("Warning", "Select at least one game")
            return
        
        self.log_text.delete(1.0, tk.END)
        self.progress['value'] = 0
        self._log_message(f"Organizing {len(selected)} game(s)...")
        
        self.organizer_thread = GamebaseOrganizationThread(
            self.games,
            self.destination_dir,
            self.template_var.get(),
            self.operation_var.get() == "move",
            self.keep_zipped_var.get(),
            self.output_queue
        )
        self.organizer_thread.start()
        self.cancel_button.config(state=tk.NORMAL)
    
    def _cancel_operation(self):
        """Cancel currently running operation."""
        if self.scanner_thread and self.scanner_thread.is_alive():
            self.scanner_thread.stop_flag.set()
            self._log_message("Cancelling scan...")
        
        if self.organizer_thread and self.organizer_thread.is_alive():
            self.organizer_thread.stop_flag.set()
            self._log_message("Cancelling organization...")
        
        self.cancel_button.config(state=tk.DISABLED)
    
    def _save_cache(self, cache_file: Path):
        """Save scanned game metadata to cache file."""
        try:
            cache_data = [asdict(game) for game in self.games]
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            self._log_message(f"Saved cache with {len(cache_data)} entries")
        except Exception as e:
            self._log_message(f"Cache save error: {e}")
    
    def _log_message(self, msg: str):
        """Add log message."""
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)


def main():
    """Launch application."""
    root = tk.Tk()
    app = GamebaseGameOrganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
