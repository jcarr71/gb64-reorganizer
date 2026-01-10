# Version Management Guide

## Available Versions

### v1.0.0 (Stable - Current Default)
**Status:** Released and tagged on GitHub
**Features:**
- Core game organizing from zip files
- VERSION.NFO metadata extraction
- Fixed folder structure: Genre/SubGenre/Language/GameName
- Multi-disk game file renaming
- Copy/Move operations

**Access:** `git checkout v1.0.0`

---

### v1.0.1 (Current Development)
**Status:** Released and tagged on GitHub
**New Features:**
- ✨ **Dynamic Template System** - Customize folder structure with placeholders
- ✨ **15 Metadata Field Placeholders** - Build custom organization schemes:
  - `{name}`, `{primary_genre}`, `{secondary_genre}`, `{language}`
  - `{published_year}`, `{publisher}`, `{developer}`
  - `{players}`, `{control}`, `{pal_ntsc}`
  - `{unique_id}`, `{coding}`, `{graphics}`, `{music}`, `{comment}`
- ✨ **Game Name Subfolders** - All game files organized in dedicated folders
- ✨ **Template Input Field** - GUI field with help dialog showing available placeholders

**Example Templates:**
```
{primary_genre}/{secondary_genre}/{language}/{name}
{published_year}/{primary_genre}/{name}
{publisher}/{name}
{unique_id}/{name}
```

**Access:** `git checkout v1.0.1` or `git checkout main`

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
