# Version Management Guide - GameBase64 Organizer

## Available Versions


### v1.3.2 (Latest Release - **RECOMMENDED**)
**Status:** Released and tagged on GitHub
**Component:** CLI only (`gb64_reorganizer.py`) + GUI experimental (`gb64_gui.py`)
**Features:**
- ✅ All features from v1.3.1
- ✅ Additional bug fixes and improvements
- ✅ See release_notes_v1.3.2.txt for full details

**New in v1.3.2:**
- See release_notes_v1.3.2.txt for the latest changes and fixes.

**Command-Line Options:**
```bash
# Interactive mode
python gb64_reorganizer.py

# Quick mode
python gb64_reorganizer.py "C:\Source" "C:\Dest"

# With custom template
python gb64_reorganizer.py "C:\Source" "C:\Dest" --template "{publisher}/{name}"

# English games only
python gb64_reorganizer.py "C:\Source" "C:\Dest" --english-only

# Keep files zipped
python gb64_reorganizer.py "C:\Source" "C:\Dest" --keep-zipped

# Multiple options
python gb64_reorganizer.py "C:\Source" "C:\Dest" --template "{publisher}/{name}" --english-only --collapse-publishers
```

**Example Templates:**
```
{primary_genre}/{secondary_genre}/{language}/{name}  (default)
{published_year}/{primary_genre}/{name}
{publisher}/{name}
{language}/{publisher}/{primary_genre}/{name}
```

**Access:** `git checkout v1.3.2` or current `main` branch

---


### v1.3.1 (Previous Release)
**Status:** Superseded by v1.3.2
**Features:**
- See release_notes_v1.3.1.txt for details.

**Access:** `git checkout v1.3.1`

---


### v1.3.0 (Previous Release)
**Status:** Superseded by v1.3.1
**Features:**
- See release_notes_v1.3.0.txt for details.

**Access:** `git checkout v1.3.0`

---

### GUI (Work in Progress - Experimental)
**Status:** Development/Testing
**Component:** GUI only (`gb64_gui.py`)
**⚠️ Warning:** Experimental features, use with caution
**Experimental Features:**
- 🧪 Background scanning with progress tracking
- 🧪 Metadata caching (may have bugs with large collections)
- 🧪 Cancel operation support
- 🧪 Game filtering by genre/language/publisher
- 🧪 Selective organization with checkboxes
- 🧪 Batch UI updates (every 10 files)

**Known Issues:**
- Cache may not update correctly for modified files
- Large collections (30k+ files) not fully tested
- UI may freeze on very large selections

**Recommendation:** Use v1.3.0 CLI for production use

**Access:** Current `main` branch (not tagged)

---


### v1.2.1 (Previous Release)
**Status:** Superseded by v1.3.0

---

### v1.2.0 (Previous Release)
**Status:** Superseded by v1.2.1
**Features:**
- Template system
- Path sanitization for special characters

**Access:** `git checkout v1.2.0`

---

### v1.0.1 (Legacy)
**Status:** Deprecated
**Features:**
- Original template system

**Access:** `git checkout v1.0.1`

---

### v1.0.0 (Legacy)
**Status:** Deprecated
**Features:**
- Fixed folder structure only

**Access:** `git checkout v1.0.0`

---

## How to Switch Versions

### Check out latest version (1.3.1)
```bash
git checkout v1.3.1
```

### Check out version 1.2.1
```bash
git checkout v1.2.1
```

### Check out version 1.2.0
```bash
git checkout v1.2.0
```

### Check out version 1.0.1
```bash
git checkout v1.0.1
```

### Check out version 1.0.0
```bash
git checkout v1.0.0
```

### View version history
```bash
git log --oneline --graph --all
```

### List all tags
```powershell
git tag -l -n5
```

---

## GitHub Release Pages

All versions are available as GitHub Releases at:
https://github.com/jcarr71/gb64-reorganizer/releases

- **v1.3.1** - Current stable CLI with published_year fix for non-numeric years
- **v1.3.0** - Previous stable CLI with advanced options and bug fixes
- **v1.2.1** - Legacy stable release
- **v1.0.1** - Legacy version with basic template system
- **v1.0.0** - Original stable release with fixed structure

---

## Development Workflow

### For v1.3.1+ development:
1. Develop on `main` branch
2. When ready to release, commit changes: `git commit -m "..."`
3. Create annotated tag: `git tag -a vX.X.X -m "Release notes"`
4. Push to GitHub: `git push origin main --tags`

### To keep all versions available:
All version tags are preserved on GitHub and can be checked out anytime using `git checkout vX.X.X`.

---

## File Structure by Version

### v1.3.1
- `gb64_reorganizer.py` (with template system, English filter, publisher collapse, keep-zipped, published_year sanitization)
- `gb64_gui.py` (experimental GUI with filtering and caching)
- `.github/copilot-instructions.md` (developer documentation)
- `.gitignore` (proper Git configuration)

### v1.2.1
- `gb64_reorganizer.py` (with template system)
- `gb64_gui.py` (experimental GUI)
- `.github/copilot-instructions.md`
- `.gitignore`

### v1.0.1
- `gb64_reorganizer.py` (with template system)
- `gb64_gui.py` (new GUI with template field)
- `.github/copilot-instructions.md`
- `.gitignore`

### v1.0.0
- `gb64_reorganizer.py` (core organizer, no template system)
- Fixed folder structure only

### v1.0.1
- `gb64_reorganizer.py` (with template system)
- `gb64_gui.py` (new GUI with template field)
- `.github/copilot-instructions.md` (developer notes)
- `.gitignore` (proper Git configuration)

---

## Backup Strategy

✅ **GitHub is your backup:**
- All versions tagged and pushed
- Full commit history preserved
- Can recover any version instantly
- Releases page shows all available versions

No additional backup needed - GitHub provides complete version history!
