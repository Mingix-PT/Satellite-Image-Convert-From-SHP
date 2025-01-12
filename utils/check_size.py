import os
from PIL import Image
import rasterio

def get_image_sizes(folder_path):
  unique_sizes = set()

  for root, dirs, files in os.walk(folder_path):
    for filename in files:
      if filename.lower().endswith(('.tif')):
        image_path = os.path.join(root, filename)
        with rasterio.open(image_path) as src:
            unique_sizes.add((src.shape[0], src.shape[1], src.count))

  return unique_sizes

if __name__ == '__main__':
  folder_path = 'gg_earth_cut64_dataset'
  sizes = get_image_sizes(folder_path)

  print("Unique image sizes:")
  for size in sizes:
    print(size)
