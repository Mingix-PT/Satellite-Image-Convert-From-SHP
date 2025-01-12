import os
import rasterio
import numpy as np
from shutil import copyfile

input_folder = 'sentinel/dataset_cut'
output_folder = input_folder + '_filtered'

input_file_count = len([name for name in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, name)) and name.endswith('.tif') and name.startswith('HoangHoa')])
print(f"Number of files in input folder: {input_file_count}")

if not os.path.exists(output_folder):
  os.makedirs(output_folder)

for filename in os.listdir(input_folder):
  if filename.endswith('.tif'):
    filepath = os.path.join(input_folder, filename)
    with rasterio.open(filepath) as src:
      image = src.read([1, 2, 3])  # Read only the first 3 channels
      black_pixels = np.sum((image[0] == 0 and image[1] == 0 and image[2] == 0))
      print(f"{filename}: {black_pixels} black pixels")
      total_pixels = image.shape[1] * image.shape[2]
      black_pixel_rate = black_pixels / total_pixels
      print(f"{filename}: {black_pixel_rate:.2f} black pixels")
      if black_pixel_rate <= 0.3:
        mask_file = filename.replace('_sat.tif', '_mask.png')
        copyfile(filepath, os.path.join(output_folder, filename))
        copyfile(os.path.join(input_folder, mask_file), os.path.join(output_folder, mask_file))

file_count = len([name for name in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, name))])
print(f"Number of files in output folder: {file_count}")
