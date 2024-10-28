import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import shutil
import glob

os.environ['SHAPE_RESTORE_SHX'] = 'YES'

# Specify the paths
data_dir = 'final'
mask_dir = f'{data_dir}_mask_new'
target_dir = f'{data_dir}_dataset_new'

def find_tif_files(directory):
    tif_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.tif'):
                file_path = os.path.join(root, file)
                tif_files.append(file_path)
    return tif_files

tif_files = find_tif_files(data_dir)
print(f"Found {len(tif_files)} TIF files.")

def save_files_to_directory(files, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for file in files:
        if os.path.isfile(file):
            base_name, ext = os.path.splitext(os.path.basename(file))
            new_name = f"{base_name}_sat{ext}" if ext.lower() == '.tif' else f"{base_name}{ext}"
            new_file_path = os.path.join(target_dir, new_name)
            shutil.copy(file, new_file_path)
            print(f"Copied {file} to {new_file_path}")

save_files_to_directory(tif_files, target_dir)

def find_files_with_pattern(directory, pattern):
    search_pattern = os.path.join(directory, '**', pattern)
    matching_files = glob.glob(search_pattern, recursive=True)
    return matching_files

from rasterio.features import rasterize
from PIL import Image

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
            shapefiles[cls] = gpd.read_file(shapefile_paths[cls])
            print(f"Loaded shapefile '{cls}' for path '{shapefile_paths[cls]}'")
        else:
            print(f"Warning: No shapefile found for class '{cls}'")

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
        for geom in shapefile.geometry:
            if geom.is_valid:
                # Rasterize the geometry and add it to the image
                mask = rasterio.features.geometry_mask([geom], transform=transform, invert=True, out_shape=(height, width))
                img[mask] = color

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
    output_png = os.path.join(mask_dir, f"{pattern}_mask.png")
    shapefile_paths = {cls: os.path.join(data_dir, f"{pattern}_{cls}.shp") for cls in classes}
    merge_shapefiles_to_png(classes, shapefile_paths, tif_file, output_png, class_colors)

def copy_files(src_folder, dst_folder):
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    for filename in os.listdir(src_folder):
        src_file = os.path.join(src_folder, filename)
        dst_file = os.path.join(dst_folder, filename)
        if os.path.isfile(src_file):
            shutil.copy(src_file, dst_file)
            print(f"Copied {src_file} to {dst_file}")

copy_files(mask_dir, target_dir)
