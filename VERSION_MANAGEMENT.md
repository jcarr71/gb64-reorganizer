# Version Management Guide - GameBase64 Organizer

## Available Versions

### v1.2.0 (Stable CLI - **RECOMMENDED**)
**Status:** Released and tagged on GitHub
**Component:** CLI only (`gb64_reorganizer.py`)
**Features:**
- ✅ Core game organizing from zip files
- ✅ VERSION.NFO metadata extraction (15 fields)
- ✅ **Dynamic Template System** - Customize folder structure with placeholders
- ✅ **15 Metadata Field Placeholders:**
  - `{name}`, `{primary_genre}`, `{secondary_genre}`, `{language}`
  - `{published_year}`, `{publisher}`, `{developer}`
  - `{players}`, `{control}`, `{pal_ntsc}`
  - `{unique_id}`, `{coding}`, `{graphics}`, `{music}`, `{comment}`
- ✅ **Path Sanitization Fix** - Handles slashes in metadata (e.g., "English \ Italian" → "English - Italian")
- ✅ **Template Validation** - Helpful error messages for typos in field names
- ✅ Interactive template prompt with examples
- ✅ Multi-disk game file renaming
- ✅ Copy/Move operations

**Example Templates:**
```
{primary_genre}/{secondary_genre}/{language}/{name}  (default)
{published_year}/{primary_genre}/{name}
{publisher}/{name}
{language}/{publisher}/{primary_genre}/{secondary_genre}
```

**Access:** `git checkout v1.2.0`

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

**Recommendation:** Use v1.2.0 CLI for production use

**Access:** Current `main` branch (not tagged)

---

### v1.0.1 (Previous Release)
**Status:** Superseded by v1.2.0
**Features:**
- Template system (basic version)
- Path issues with special characters

**Access:** `git checkout v1.0.1`

---

### v1.0.0 (Legacy)
**Status:** Deprecated
**Features:**
- Fixed folder structure only

**Access:** `git checkout v1.0.0`

---

## How to Switch Versions

### Check out version 1.0.0
```powershell
git checkout v1.0.0
```

### Check out version 1.0.1 (latest)
```powershell
git checkout v1.0.1
# or
git checkout main
```

### View version history
```powershell
git log --oneline --graph --all
```

### List all tags
```powershell
git tag -l -n5
```

---

## GitHub Release Pages

Both versions are available as GitHub Releases at:
https://github.com/jcarr71/gb64-reorganizer/releases

- **v1.0.0** - Original stable release
- **v1.0.1** - Latest with template system

---

## Development Workflow

### For version 1.0.1+ development:
1. Develop on `main` branch
2. When ready to release, commit changes: `git commit -m "..."`
3. Create annotated tag: `git tag -a vX.X.X -m "Release notes"`
4. Push to GitHub: `git push origin main --tags`

### To keep 1.0.0 available:
The v1.0.0 tag ensures the exact commit is preserved on GitHub and can be checked out anytime.

---

## File Structure by Version

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
