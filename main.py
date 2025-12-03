import sys
import os
import exiftool
from datetime import datetime, timezone

# Quit if images path is not provided
if len(sys.argv) == 1:
  print('Missing media path')
  sys.exit(1)

# Set images path
media_path = sys.argv[1]

def get_all_files():
    """Get all files from media_path."""
    files = []

    if (os.path.isdir(media_path)):
        for dirname, dirnames, filenames in os.walk(media_path):
            for filename in filenames:
                files.append(os.path.join(dirname, filename))
    else:
        files.append(media_path)

    return files

def get_metadata(files):
    """Get metadata from files in batch."""
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(files)

    return metadata

def get_new_path(orig_path, created_time):
    """Build new filename based on EXIF data using UTC time in format YYYY-MM-DD_HH-MM-SS.microseconds."""
    file_dir = os.path.dirname(orig_path)
    filename = os.path.basename(orig_path)
    filename_without_extension, file_extension = os.path.splitext(filename)

    s = str(created_time)

    dt = None
    # Try ISO-like normalization first (handles EXIF "YYYY:MM:DD HH:MM:SS[.micro][+/-HH:MM]")
    try:
        normalized = s.replace(':', '-', 2).replace(' ', 'T', 1)
        dt = datetime.fromisoformat(normalized)
    except Exception:
        # Fallback strptime attempts for common patterns
        for fmt in (
            '%Y:%m:%d %H:%M:%S.%f%z',
            '%Y:%m:%d %H:%M:%S.%f',
            '%Y:%m:%d %H:%M:%S%z',
            '%Y:%m:%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f%z',
            '%Y-%m-%d %H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
        ):
            try:
                dt = datetime.strptime(s, fmt)
                break
            except Exception:
                continue

    if dt is None:
        # Last-resort: extract digits and build a reasonable datetime (YYYYMMDDHHMMSS)
        digits = ''.join(filter(str.isdigit, s))
        digits = digits.ljust(14, '0')[:14]
        dt = datetime.strptime(digits, '%Y%m%d%H%M%S')

    # Make timezone-aware (assume local if naive), then convert to UTC
    if dt.tzinfo is None:
        local_tz = datetime.now().astimezone().tzinfo
        dt = dt.replace(tzinfo=local_tz)
    dt_utc = dt.astimezone(timezone.utc)

    new_filename = dt_utc.strftime('%Y-%m-%d_%H%M%S.%f')
    new_path = new_filename + '_' + filename_without_extension + file_extension

    return os.path.join(file_dir, new_path)

files = get_all_files()
metadata = get_metadata(files)

total = len(metadata)
for idx, d in enumerate(metadata, start=1):
    path = d["SourceFile"]

    try:
        if 'EXIF:DateTimeOriginal' in d:
            created_time = d['EXIF:DateTimeOriginal']
        elif 'XMP:DateTimeOriginal' in d:
            created_time = d['XMP:DateTimeOriginal']
        elif 'File:FileModifyDate' in d:
            created_time = d['File:FileModifyDate']

        new_path = get_new_path(path, created_time)

        print(f'[{idx}/{total}] {path} -> {new_path}')

        os.rename(path, new_path)
    except Exception as e:
        print(f'[{idx}/{total}] Error loading data for {path}')
