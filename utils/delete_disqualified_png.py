import os
from PIL import Image

folder_path = 'final_dataset_filtered'
folder_path2 = 'img_n_gt'

def is_corrupted(image_path):
  try:
    with Image.open(image_path) as img:
      img.verify()  # Verify that it is, in fact, an image
    return False
  except (IOError, SyntaxError):
    return True

def black_pixel_rate(image_path):
  with Image.open(image_path) as img:
    img = img.convert('L')  # Convert to grayscale
    pixels = list(img.getdata())
    black_pixels = pixels.count(0)
    total_pixels = len(pixels)
    return black_pixels / total_pixels

for filename in os.listdir(folder_path):
  if filename.endswith('.png'):
    base_name = os.path.splitext(filename)[0].replace('_mask', '')
    mask_file_path = os.path.join(folder_path, filename)
    tif_file_path = mask_file_path.replace('_mask.png', '_sat.tif')
    plot_file_path = os.path.join(folder_path2, base_name + '.png')

    if is_corrupted(mask_file_path):
      print(f"Deleting corrupted file: {mask_file_path}")
      os.remove(mask_file_path)
      os.remove(tif_file_path)
      os.remove(plot_file_path)
    elif black_pixel_rate(mask_file_path) >= 0.2:
      print(f"Deleting file with high black pixel rate: {mask_file_path}")
      os.remove(mask_file_path)
      os.remove(tif_file_path)
      os.remove(plot_file_path)

# Count the number of remaining files in the folder
print(f"Number of files in the folder: {len(os.listdir(folder_path))}")
print(f"Number of files in the folder2: {len(os.listdir(folder_path2))}")
