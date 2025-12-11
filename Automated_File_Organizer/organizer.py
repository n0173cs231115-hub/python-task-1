#!/usr/bin/env python3
\"\"\"Automated File Organizer

Scans a source directory and organizes files into category folders based on extension.
Features:
 - Uses pathlib for safe path handling
 - Maps extensions to categories (configurable)
 - Dry-run mode to preview changes
 - Conflict resolution by appending incrementing suffix (name (1).ext)
 - Logging to file and console
 - Summary report printed at the end
\"\"\"
from pathlib import Path
import argparse
import shutil
import logging
import sys
from collections import defaultdict

# Default category mapping - extendable
CATEGORIES = {
    '.py': 'Python_Code',
    '.ipynb': 'Notebooks',
    '.txt': 'Documents',
    '.md': 'Documents',
    '.pdf': 'Documents',
    '.docx': 'Documents',
    '.xlsx': 'Spreadsheets',
    '.csv': 'Spreadsheets',
    '.png': 'Images',
    '.jpg': 'Images',
    '.jpeg': 'Images',
    '.gif': 'Images',
    '.bmp': 'Images',
    '.mp3': 'Audio',
    '.wav': 'Audio',
    '.mp4': 'Video',
    '.mov': 'Video',
    '.zip': 'Archives',
    '.tar': 'Archives',
    '.gz': 'Archives',
    '.json': 'Data',
    '.xml': 'Data',
    '.html': 'Web',
    '.css': 'Web',
    '.js': 'Web',
    # add more as needed
}

LOG_FILE_NAME = 'organizer.log'

def configure_logging(log_path: Path, verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[
            logging.FileHandler(str(log_path), encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def resolve_conflict(target: Path) -> Path:
    \"\"\"If target path exists, append ' (1)', ' (2)', ... before the suffix.\"\"\"
    parent = target.parent
    stem = target.stem
    suffix = target.suffix
    counter = 1
    new_target = parent / f\"{stem} ({counter}){suffix}\"
    while new_target.exists():
        counter += 1
        new_target = parent / f\"{stem} ({counter}){suffix}\"
    return new_target

def is_same_file(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except Exception:
        return False

def organize_directory(source: Path, dry_run: bool=False, include_hidden: bool=False):
    if not source.exists():
        logging.error("Source directory does not exist: %s", source)
        return None

    moved = []
    errors = []
    skipped = []
    total_files = 0
    # Walk recursively
    for item in source.rglob('*'):
        try:
            # Skip directories and symlinks
            if item.is_dir() or item.is_symlink():
                continue
            # Optionally skip hidden files (starting with .) unless include_hidden True
            if not include_hidden and item.name.startswith('.'):
                skipped.append(item)
                continue
            total_files += 1
            ext = item.suffix.lower()
            category = CATEGORIES.get(ext, 'Other')
            target_dir = source / category
            if not target_dir.exists():
                logging.info("Creating directory: %s", target_dir)
                if not dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)

            target_path = target_dir / item.name

            # If the file is already inside its target directory, skip
            if is_same_file(item, target_path):
                logging.debug("Skipping (already in place): %s", item)
                continue

            if target_path.exists():
                logging.info("Conflict detected for %s -> %s", item, target_path)
                target_path = resolve_conflict(target_path)
                logging.info("Resolved conflict to: %s", target_path)

            logging.info("Moving: %s -> %s", item, target_path)
            if not dry_run:
                # Use shutil.move which can handle across-device moves
                shutil.move(str(item), str(target_path))
            moved.append((item, target_path))
        except PermissionError as pe:
            logging.exception("PermissionError processing %s: %s", item, pe)
            errors.append((item, str(pe)))
        except (FileNotFoundError, OSError) as e:
            logging.exception("OS error processing %s: %s", item, e)
            errors.append((item, str(e)))
        except Exception as ex:
            logging.exception("Unexpected error processing %s: %s", item, ex)
            errors.append((item, str(ex)))

    # Summary
    summary = {
        'total_files_seen': total_files,
        'moved_count': len(moved),
        'errors_count': len(errors),
        'skipped_count': len(skipped)
    }
    logging.info("=== Summary ===")
    logging.info("Total files scanned: %d", total_files)
    logging.info("Files moved: %d", len(moved))
    logging.info("Errors: %d", len(errors))
    logging.info("Skipped (hidden or ignored): %d", len(skipped))

    return {
        'moved': moved,
        'errors': errors,
        'skipped': skipped,
        'summary': summary
    }

def parse_args():
    parser = argparse.ArgumentParser(description='Automated File Organizer')
    parser.add_argument('source', help='Source directory to organize', type=Path)
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without moving files')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging to console')
    parser.add_argument('--include-hidden', action='store_true', help='Include hidden files (dotfiles)')
    parser.add_argument('--log-file', default=LOG_FILE_NAME, help='Log file name/path')
    parser.add_argument('--list-only', action='store_true', help='Only list files and categories (no changes) [alias to --dry-run]')
    return parser.parse_args()

def main():
    args = parse_args()
    src: Path = args.source
    dry_run = args.dry_run or args.list_only
    log_path = src / args.log_file if src.exists() else Path(args.log_file)
    configure_logging(log_path, args.verbose)
    logging.info("Starting organizer on: %s (dry_run=%s)", src, dry_run)
    result = organize_directory(src, dry_run=dry_run, include_hidden=args.include_hidden)
    if result is None:
        print(\"No result - possibly invalid source path.\")
        return

    # Print a brief summary for user
    s = result['summary']
    print(\"\\n=== Organizer Summary ===\")
    print(f\"Total scanned: {s['total_files_seen']}\")
    print(f\"Moved: {s['moved_count']}\")
    print(f\"Errors: {s['errors_count']}\")
    print(f\"Skipped: {s['skipped_count']}\")
    print(f\"Log file: {log_path}\")
    logging.info(\"Finished organizer run.\")

if __name__ == '__main__':
    main()
