import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import shutil
import glob

# os.environ['SHAPE_RESTORE_SHX'] = 'YES'

# Specify the paths
data_dir = 'final_sample'
mask_dir = f'{data_dir}_mask_new'
target_dir = f'{data_dir}_dataset_new'
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
            print(f"Copied {file} to {new_file_path}")

def find_files_with_pattern(directory, pattern):
    search_pattern = os.path.join(directory, '**', pattern)
    matching_files = glob.glob(search_pattern, recursive=True)
    return matching_files

def merge_shapefiles_to_png(classes, shapefile_paths, tif_path, output_png, class_colors):
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

    img = np.zeros((height, width, 3), dtype=np.uint8)

    for cls, shapefile in shapefiles.items():
        if shapefile.crs != src.crs:
            shapefiles[cls] = shapefile.to_crs(src.crs)
            print(f"Reprojected '{cls}' shapefile to match TIFF CRS.")
        color = class_colors[cls]
        for geom in shapefile.geometry:
            mask = rasterio.features.geometry_mask([geom], transform=transform, invert=True, out_shape=(height, width), all_touched=True)
            img[mask] = color

    plt.imsave(output_png, img)
    print(f"Saved PNG image to: {output_png}")

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

    for cls, shapefile in shapefiles.items():
        for idx, geom in enumerate(shapefile.geometry):
            if geom.is_valid:
                mask = rasterio.features.geometry_mask(
                    [geom],
                    transform=transform,
                    invert=True,
                    out_shape=(height, width),
                    all_touched=True
                )

                mask_img = (mask.astype(np.uint8) * 255)

                if not os.path.exists(png_folder):
                    os.makedirs(png_folder)
                output_path = f"{png_folder}/{cls}_mask_{idx}.png"

                plt.imsave(output_path, mask_img, cmap='gray')
                print(f"Saved mask for '{cls}' geometry {idx} to {output_path}")

def combine_pngs(png_folder, output_combined_png):
    image_size = Image.open(os.path.join(png_folder, os.listdir(png_folder)[0])).size
    combined_image = np.zeros((image_size[1], image_size[0], 3), dtype=np.uint8)

    for filename in os.listdir(png_folder):
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
        'unidentifiable': (0, 0, 0)
    }

    if not os.path.exists(mask_dir):
        os.makedirs(mask_dir)

    for tif_file in tif_files:
        pattern = os.path.splitext(os.path.basename(tif_file))[0]
        output_png = os.path.join(mask_dir, f"{pattern}_mask.png")
        shapefile_paths = {cls: os.path.join(data_dir, f"{pattern}_{cls}.shp") for cls in classes}
        merge_shapefiles_to_png(classes, shapefile_paths, tif_file, output_png, class_colors)
        save_individual_masks(classes, shapefile_paths, tif_file, mask_dir)

    output_combined_png = 'combined_output.png'
    combine_pngs(png_folder, output_combined_png)

    copy_files(mask_dir, target_dir)
