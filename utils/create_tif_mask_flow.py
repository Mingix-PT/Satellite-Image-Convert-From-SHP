import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import os
import numpy as np
from PIL import Image, ImageFile
import matplotlib.pyplot as plt
import shutil
import glob
import shapefile
from rasterio.features import geometry_mask
from shapely.geometry import shape
from shapefile import Reader

# Increase the maximum image size limit
Image.MAX_IMAGE_PIXELS = None

# Suppress the DecompressionBombWarning
ImageFile.LOAD_TRUNCATED_IMAGES = True

# os.environ['SHAPE_RESTORE_SHX'] = 'YES'

# Specify the paths
data_dir = 'sentinel/25km/data'
mask_dir = f'{data_dir}_mask'
target_dir = f'{data_dir}_dataset'
png_folder = f'{data_dir}_individual_masks'

def find_tif_files(directory):
    tif_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.tif'):
                file_path = os.path.join(root, file)
                tif_files.append(file_path)
    return tif_files

def save_files_to_directory(files, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for file in files:
        if os.path.isfile(file):
            base_name, ext = os.path.splitext(os.path.basename(file))
            new_name = f"{base_name}_sat{ext}" if ext.lower() == '.tif' else f"{base_name}{ext}"
            new_file_path = os.path.join(target_dir, new_name)
            shutil.copy(file, new_file_path)
            # print(f"Copied {file} to {new_file_path}")

def find_files_with_pattern(directory, pattern):
    search_pattern = os.path.join(directory, '**', pattern)
    matching_files = glob.glob(search_pattern, recursive=True)
    return matching_files

def merge_shapefiles_to_png(classes, shapefile_paths, tif_path, output_png, class_colors):
    print(f"Creating PNG from TIF file '{tif_path}'")
    shapefiles = {}
    for cls in classes:
        if cls in shapefile_paths and os.path.exists(shapefile_paths[cls]):
            shapefiles[cls] = gpd.read_file(shapefile_paths[cls])
            # print(f"Loaded shapefile '{cls}' for path '{shapefile_paths[cls]}'")
        else:
            print(f"Warning: No shapefile found for class '{cls}'")

    with rasterio.open(tif_path) as src:
        transform = src.transform
        width = src.width
        height = src.height
        tif_crs = src.crs

    img = np.zeros((height, width, 3), dtype=np.uint8)

    for cls, shapefile in shapefiles.items():
        color = class_colors[cls]
        print(f'{cls}: {len(shapefile.geometry)}')

        # Check and reproject shapefile geometries if necessary
        if shapefile.crs != tif_crs:
            print(f"Reprojecting shapefile '{cls}' to match TIF CRS")
            shapefile = shapefile.to_crs(tif_crs)

        for geom in shapefile.geometry:
            # print(geom)
            mask = rasterio.features.geometry_mask(
                [geom],
                transform=transform,
                invert=True,
                out_shape=(height, width),
                all_touched=True)
            # print(np.sum(mask))
            img[mask] = color

    Image.fromarray(img).save(output_png)
    print(f"Saved PNG to {output_png}")

def save_individual_masks(classes, shapefile_paths, tif_path, output_dir):
    shapefiles = {}
    for cls in classes:
        if cls in shapefile_paths:
            shapefiles[cls] = gpd.read_file(shapefile_paths[cls])
            print(f"Loaded shapefile '{cls}' for path '{shapefile_paths[cls]}'")
        else:
            print(f"Warning: No shapefile found for class '{cls}'")

    with rasterio.open(tif_path) as src:
        transform = src.transform
        width = src.width
        height = src.height

    total_shp = 0
    for cls, shapefile in shapefiles.items():
        total_shp += len(shapefile.geometry)
        for idx, geom in enumerate(shapefile.geometry):
            if geom.is_valid:
                mask = rasterio.features.geometry_mask(
                    [geom],
                    transform=transform,
                    invert=True,
                    out_shape=(height, width),
                    all_touched=False
                )

                mask_img = (mask.astype(np.uint8) * 255)

                if not os.path.exists(png_folder):
                    os.makedirs(png_folder)
                output_path = f"{png_folder}/{cls}_mask_{idx}.png"

                plt.imsave(output_path, mask_img, cmap='gray')
                # print(f"Saved mask for '{cls}' geometry {idx} to {output_path}")
            else:
                print(f"Skipping invalid geometry for '{cls}' geometry {idx}: {geom.is_valid}")

def combine_pngs(png_folder, output_combined_png, class_name=None):
    image_size = Image.open(os.path.join(png_folder, os.listdir(png_folder)[0])).size
    combined_image = np.zeros((image_size[1], image_size[0], 3), dtype=np.uint8)

    for filename in os.listdir(png_folder):
        if class_name and not filename.startswith(class_name):
            continue
        if filename.endswith(".png"):
            mask = np.array(Image.open(os.path.join(png_folder, filename)).convert("RGB"))
            combined_image = np.maximum(combined_image, mask)

    Image.fromarray(combined_image).save(output_combined_png)
    print(f"Saved combined PNG to {output_combined_png}")


def copy_files(src_folder, dst_folder):
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    for filename in os.listdir(src_folder):
        src_file = os.path.join(src_folder, filename)
        dst_file = os.path.join(dst_folder, filename)
        if os.path.isfile(src_file):
            shutil.copy(src_file, dst_file)
            print(f"Copied {src_file} to {dst_file}")

if __name__ == "__main__":
    tif_files = find_tif_files(data_dir)
    print(f"Found {len(tif_files)} TIF files.")

    save_files_to_directory(tif_files, target_dir)

    classes = ['bamboo', 'forest', 'rice_field', 'water', 'residential', 'unidentifiable']
    classes.sort()
    class_colors = {
        'bamboo': (0, 0, 255),
        'forest': (0, 255, 0),
        'rice_field': (255, 0, 0),
        'water': (0, 255, 255),
        'residential': (255, 255, 0),
        'unidentifiable': (255, 255, 255)
    }

    if not os.path.exists(mask_dir):
        os.makedirs(mask_dir)

    for tif_file in tif_files:
        pattern = os.path.splitext(os.path.basename(tif_file))[0]
        output_png = os.path.join(mask_dir, f"{pattern}_mask.png")
        shapefile_paths = {cls: os.path.join(data_dir, f"{pattern}_{cls}.shp") for cls in classes}
        output_combined_png = 'combined_output.png'
        merge_shapefiles_to_png(classes, shapefile_paths, tif_file, output_png, class_colors)
        # save_individual_masks(classes, shapefile_paths, tif_file, png_folder)
        # combine_pngs(png_folder, output_combined_png)

    copy_files(mask_dir, target_dir)
