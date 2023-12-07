import os
from PIL import Image, ExifTags

tag_to_code = {v: k for k, v in ExifTags.TAGS.items()}
codes_for_date_time = [tag_to_code['DateTime']]

images_path = 'images'

with os.scandir(images_path) as it:
    for entry in it:
        if entry.is_file():
            img = Image.open(entry.path)
            img_exif = img.getexif()

            if img_exif is None:
                continue
            

            for code in codes_for_date_time:    
              if code in img_exif:
                  file_dir = os.path.dirname(entry.path)
                  filename, file_extension = os.path.splitext(entry.path)
                  new_filename = str(img_exif[code]).replace(' ', '_').replace(':', '')
                  new_path = os.path.join(file_dir, new_filename + file_extension)

                  print('Renaming', entry.path, 'to', new_path)

                  os.rename(entry.path, new_path)
