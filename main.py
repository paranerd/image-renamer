import sys
import os
import exiftool

# Quit if images path is not provided
if len(sys.argv) == 1:
  print('Missing media path')
  sys.exit(1)

# Set images path
media_path = sys.argv[1]

def get_all_files():
    """Get all files from media_path."""
    files = []

    for dirname, dirnames, filenames in os.walk(media_path):
        for filename in filenames:
            files.append(os.path.join(dirname, filename))

    return files

def get_metadata(files):
    """Get metadata from files in batch."""
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(files)

    return metadata

def get_new_path(orig_path, created_time):
    """Build new filename based on EXIF data."""
    file_dir = os.path.dirname(orig_path)
    filename = os.path.basename(orig_path)
    filename_without_extension, file_extension = os.path.splitext(filename)

    # Only keep the numbers
    new_filename = str(created_time).replace(' ', '_')
    new_filename = ''.join(filter(str.isdigit, new_filename))[:14]

    new_path = new_filename + '_' + filename_without_extension + file_extension

    return os.path.join(file_dir, new_path)

files = get_all_files()
metadata = get_metadata(files)

for d in metadata:
    path = d["SourceFile"]

    try:
        if 'EXIF:DateTimeOriginal' in d:
            created_time = d['EXIF:DateTimeOriginal']
        elif 'File:FileModifyDate' in d:
            created_time = d['File:FileModifyDate']

        new_path = get_new_path(path, created_time)

        print(path, '| Renaming to', new_path)

        os.rename(path, new_path)
    except Exception as e:
        print('Error loading data')
