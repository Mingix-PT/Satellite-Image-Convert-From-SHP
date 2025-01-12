import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import os
import numpy as np
from rasterio.features import rasterize
from PIL import Image
import matplotlib.pyplot as plt
import shutil
import glob

os.environ['SHAPE_RESTORE_SHX'] = 'YES'

data_dir = 'final'
tif_files = ['final/QuanSon_MONTH_12_6_3_39.tif']
mask_dir = 'wrong_masks'

def find_files_with_pattern(directory, pattern):
  search_pattern = os.path.join(directory, '**', pattern)
  print(search_pattern)
  matching_files = glob.glob(search_pattern, recursive=True)
  print(matching_files)
  return matching_files

def merge_shapefiles_to_png(classes, shapefile_paths, tif_path, output_png, class_colors):
    """
    Merges multiple shapefiles into a single PNG image based on specified class colors.

    Parameters:
    - classes: List of class names.
    - shapefile_paths: Dictionary mapping each class name to its shapefile path.
    - tif_path: Path to the reference TIFF file.
    - output_png: Path to the output PNG file.
    - class_colors: Dictionary mapping each class name to an RGB tuple.
    """
    # Load shapefiles for each class
    shapefiles = {}
    for cls in classes:
        if cls in shapefile_paths:
            if os.path.exists(shapefile_paths[cls]):
              print(f"Loading shapefile '{cls}' for path '{shapefile_paths[cls]}'")
              shapefiles[cls] = gpd.read_file(shapefile_paths[cls])
            else:
                shapefiles[cls] = None
            # print(f"Loaded shapefile '{cls}' for path '{shapefile_paths[cls]}'")

    # Use the .tif file to get the georeferencing information
    with rasterio.open(tif_path) as src:
        transform = src.transform
        crs = src.crs
        width = src.width
        height = src.height

    # Create a blank image
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # Plot each shapefile onto the image
    for cls, shapefile in shapefiles.items():
        color = class_colors[cls]
        if shapefile is None:
          print(f"Shapefile '{cls}' not found, skipping...")
          continue
        try:
          for geom in shapefile.geometry:
              if geom.is_valid:
                print(cls)
                # Rasterize the geometry and add it to the image
                mask = rasterio.features.geometry_mask([geom], transform=transform, invert=True, out_shape=(height, width))
                img[mask] = color
              else:
                print(f"Invalid geometry found in shapefile '{cls}', skipping...")
        except Exception as e:
            print(f"Error rasterizing shapefile '{cls}': {e}")

    # Save the image as a PNG file
    plt.imsave(output_png, img)
    print(f"Saved PNG image to: {output_png}")

classes = ['bamboo', 'forest', 'rice_field', 'water', 'residential', 'unidentifiable']
classes.sort()
class_colors = {
    'bamboo': (0, 0, 255),
    'forest': (0, 255, 0),
    'rice_field': (255, 0, 0),
    'water': (0, 255, 255),
    'residential': (255, 255, 0),
    'unidentifiable': (0, 0, 0)
}

if not os.path.exists(mask_dir):
    os.makedirs(mask_dir)

for tif_file in tif_files:
    pattern = os.path.splitext(os.path.basename(tif_file))[0]
    print(pattern)
    output_png = os.path.join(mask_dir, f"{pattern}_mask.png")
    current_masks = find_files_with_pattern(data_dir, f"{pattern}_*.shp")
    current_masks.sort()
    if len(current_masks) > 0:
        shapefile_paths = {cls: f"{os.path.splitext(tif_file)[0]}_{cls}.shp" for cls in classes}
        print(shapefile_paths)
        merge_shapefiles_to_png(classes, shapefile_paths, tif_file, output_png, class_colors)
