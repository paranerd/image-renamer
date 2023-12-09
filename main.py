import os
from PIL import Image, ExifTags, UnidentifiedImageError
import sys

# Quit if images path is not provided
if len(sys.argv) == 1:
  print('Missing media path')
  sys.exit(1)

# Set images path
media_path = sys.argv[1]

# Set mode
do_prefix = len(sys.argv) > 2 and sys.argv[2] == 'prefix' # Prefixes the original filename with the selected EXIF data

# Get all Exif codes relevant for Creation Date
tag_to_code = {v: k for k, v in ExifTags.TAGS.items()}
codes_for_date_time = [tag_to_code['DateTime']]

def get_exif_data(path):
    """Get EXIF data from media file."""
    img = Image.open(path)

    return img.getexif()

def get_new_path(orig_path, created_date):
    """Build new filename based on EXIF data."""
    file_dir = os.path.dirname(orig_path)
    filename = os.path.basename(orig_path)
    filename_without_extension, file_extension = os.path.splitext(filename)

    # Only keep the numbers
    new_filename = str(created_date).replace(' ', '_')
    new_filename = ''.join(filter(str.isdigit, new_filename))

    if do_prefix and new_filename != filename_without_extension:
        new_path = new_filename + '_' + filename_without_extension + file_extension
    else:
        new_path = new_filename + file_extension

    return os.path.join(file_dir, new_path)

# Loop
with os.scandir(media_path) as it:
    for entry in it:
        if not entry.is_file():
            continue
        
        try:
            img_exif = get_exif_data(entry.path)
        except UnidentifiedImageError:
            print(entry.path, '| Error: Failed reading EXIF data')

        if img_exif is None:
            print(entry.path, '| Error: No EXIF data')
            continue

        for code in codes_for_date_time:
          if code not in img_exif:
              print(entry.path, '| Error: No usable EXIF data found')

          new_path = get_new_path(entry.path, img_exif[code])

          print(entry.path, '| Renaming to', new_path)

          os.rename(entry.path, new_path)
