# python-task-1# Automated File Organizer

A small Python CLI tool that scans a directory and organizes files into folders by file type.

## Features
- Recursively scans a directory and its subdirectories.
- Maps file extensions to category folders (configurable in the script).
- Dry-run mode to preview changes without moving files.
- Handles filename conflicts by appending ` (1)`, ` (2)`, etc.
- Logs actions and errors to `organizer.log` (in the source directory by default).

## Installation
1. Requires Python 3.8+.
2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS / Linux
   venv\\Scripts\\activate   # Windows
   ```

## Usage
```bash
python organizer.py /path/to/your/folder
# Dry run (preview)
python organizer.py /path/to/your/folder --dry-run
# Verbose logging to console
python organizer.py /path/to/your/folder --verbose
# Include hidden files (dotfiles)
python organizer.py /path/to/your/folder --include-hidden
```

## Conflict resolution
If a file with the same name already exists in the category folder, the script will rename the incoming file to `name (1).ext`, `name (2).ext`, etc., until there's no conflict.

## Logs & Report
- The script writes detailed logs to `organizer.log` (by default in the source directory).
- A brief summary is printed to the console at the end of the run.

## Contributing / GitHub
1. Initialize a git repo:
   ```bash
   git init
   git add organizer.py README.md .gitignore
   git commit -m "Initial commit: Automated File Organizer"
   ```
2. Create a new repo on GitHub and follow the provided commands, e.g.:
   ```bash
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git branch -M main
   git push -u origin main
   ```

## Notes
- The extension-to-category mapping is in `organizer.py` (CATEGORIES). Edit it to suit your needs or load from a config file in future improvements.
- The script avoids moving symlinks and directories, and skips hidden files unless `--include-hidden` is set.
