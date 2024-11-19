import argparse
import os
import rasterio
import numpy as np
from PIL import Image, ImageFile
import shutil
import glob
from sklearn.model_selection import train_test_split
from rasterio.plot import reshape_as_image
import cv2

Image.MAX_IMAGE_PIXELS = None

def rotate_image(img, angle):
    # Get image dimensions
    h, w = img.shape[:2]
    # print(f"Original image shape: {img.shape}")
    center = (w // 2, h // 2)
    radians = np.deg2rad(angle)
    # print(f"Rotation angle in radians: {radians}")

    # Calculate new dimensions
    new_w = int(abs(w * np.cos(radians)) + abs(h * np.sin(radians)))
    new_h = int(abs(h * np.cos(radians)) + abs(w * np.sin(radians)))
    # print(f"New image dimensions: {new_w} x {new_h}")

    # Adjust the rotation matrix to take into account the translation
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    M[0, 2] += (new_w - w) / 2
    M[1, 2] += (new_h - h) / 2

    # Perform the rotation with the new bounding dimensions
    rotated_img = cv2.warpAffine(img, M, (new_w, new_h))
    return rotated_img, new_w, new_h

def rotate_images_in_folder(input_folder_path, output_folder_path, angle):
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    for filename in os.listdir(input_folder_path):
        if filename.endswith('.tif'):
            image_path = os.path.join(input_folder_path, filename)
            try:
                with rasterio.open(image_path) as src:
                    img = src.read()
                    img = reshape_as_image(img)  # Convert to (height, width, channels)

                # Use the function in the main code
                rotated_img, new_w, new_h = rotate_image(img, angle)
                # print(f"Rotated image shape: {rotated_img.shape}")

                # Save the rotated image using rasterio
                save_name = filename.replace('_sat.tif', '_rotated_sat.tif')
                output_image_path = os.path.join(output_folder_path, save_name)
                with rasterio.open(output_image_path, 'w', driver='GTiff', height=new_h, width=new_w, count=img.shape[2], dtype=img.dtype) as dst:
                    for i in range(img.shape[2]):
                        dst.write(rotated_img[:, :, i], i + 1)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
        elif filename.endswith('.png'):
            image_path = os.path.join(input_folder_path, filename)
            try:
                img = cv2.imread(image_path)

                # Use the function in the main code
                rotated_img, new_w, new_h = rotate_image(img, angle)
                print(f"Rotated image shape: {rotated_img.shape}")

                # Save the rotated image using OpenCV
                save_name = filename.replace('_mask.png', '_rotated_mask.png')
                output_image_path = os.path.join(output_folder_path, save_name)
                cv2.imwrite(output_image_path, rotated_img)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")

def normalize_image(image_path, output_folder=None):
    # Open the image
    if image_path.lower().endswith('.tif'):
        return

    image = Image.open(image_path)

    # Convert the image to RGB if it is not already
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert the image to a numpy array
    image_array = np.array(image)

    # Apply thresholding
    image_array = np.where(image_array > 128, 255, 0).astype(np.uint8)

    # Save the image
    new_image = Image.fromarray(image_array)
    if output_folder is None:
        output_folder = os.path.dirname(image_path)
    os.makedirs(output_folder, exist_ok=True)
    new_image.save(os.path.join(output_folder, os.path.basename(image_path)))

def normalize_images_in_folder(input_folder, output_folder=None):
  # Iterate over all files in the input folder
  for image_filename in os.listdir(input_folder):
    if image_filename.endswith('.png'):
        image_path = os.path.join(input_folder, image_filename)
        normalize_image(image_path, output_folder)


def find_files_with_pattern(directory, pattern):
    search_pattern = os.path.join(directory, '**', pattern)
    matching_files = glob.glob(search_pattern, recursive=True)
    return matching_files

def split_data(files, train_ratio=0.6, val_ratio=0.3, test_ratio=0.1):
    train_files, temp_files = train_test_split(files, test_size=(1 - train_ratio))
    val_files, test_files = train_test_split(temp_files, test_size=(test_ratio / (val_ratio + test_ratio)))
    return train_files, val_files, test_files

def copy_files_with_masks(files, destination_folder, split_folder):
    os.makedirs(destination_folder, exist_ok=True)
    for file in files:
        shutil.copy(file, destination_folder)
        # Find and copy the corresponding mask file
        base_name = os.path.basename(file).replace('_sat.tif', '')
        mask_file = os.path.join(split_folder, f'{base_name}_mask.png')
        if os.path.exists(mask_file):
            shutil.copy(mask_file, destination_folder)
        else:
            print(f"Mask file not found for {file}")

def calculate_black_pixel_rate(image_path):
    image = Image.open(image_path).convert('RGBA')  # Ensure the image has 4 channels
    image_np = np.array(image)
    total_pixels = image_np.shape[0] * image_np.shape[1]
    black_pixels = np.sum(np.all(image_np[:, :, :3] == [0, 0, 0], axis=-1))  # Ignore the alpha channel for comparison
    return black_pixels / total_pixels

def find_least_black_pixel_images(directory, top_n=10):
    image_black_pixel_rates = []

    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            image_path = os.path.join(directory, filename)
            black_pixel_rate = calculate_black_pixel_rate(image_path)
            image_black_pixel_rates.append((filename, black_pixel_rate))\

    # Filter out images with 0 black pixel rate
    image_black_pixel_rates = [item for item in image_black_pixel_rates if item[1] > 0]

    # Sort the list by black pixel rate in ascending order
    image_black_pixel_rates.sort(key=lambda x: x[1])

    # Get the top N images with the least black pixel rate
    return image_black_pixel_rates[:top_n]

def find_images_below_black_pixel_rate(directory, max_black_pixel_rate):
    image_black_pixel_rates = []

    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            image_path = os.path.join(directory, filename)
            black_pixel_rate = calculate_black_pixel_rate(image_path)
            if black_pixel_rate <= max_black_pixel_rate:
                image_black_pixel_rates.append((filename, black_pixel_rate))

    # Sort the list by black pixel rate in ascending order
    image_black_pixel_rates.sort(key=lambda x: x[1])

    return image_black_pixel_rates

def find_images_above_black_pixel_rate(directory, max_black_pixel_rate):
    image_black_pixel_rates = []

    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            image_path = os.path.join(directory, filename)
            black_pixel_rate = calculate_black_pixel_rate(image_path)
            if black_pixel_rate >= max_black_pixel_rate:
                image_black_pixel_rates.append((filename, black_pixel_rate))

    # Sort the list by black pixel rate in ascending order
    image_black_pixel_rates.sort(key=lambda x: x[1])

    return image_black_pixel_rates

def save_results_to_file(top_images, output_file='low_black_pixel_images.txt'):
    top_images.sort()
    with open(output_file, 'w') as f:
        for image, rate in top_images:
            f.write(f"{image.replace('_mask.png', '')}\n")

    print(f"The results have been saved to {output_file}")

def copy_images_to_folder(top_images, split_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for image, _ in top_images:
        tif_image = image.replace('_mask.png', '_sat.tif')
        source_path = os.path.join(split_folder, image)
        destination_path = os.path.join(output_folder, image)

        tif_source_path = os.path.join(split_folder, tif_image)
        tif_destination_path = os.path.join(output_folder, tif_image)

        shutil.copyfile(source_path, destination_path)
        shutil.copyfile(tif_source_path, tif_destination_path)

    print(f"Copied {len(top_images)} images to {output_folder}")

def cut_image(image_path, output_folder, tile_size):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if image_path.lower().endswith('.tif'):
        with rasterio.open(image_path) as raster:
            image = raster.read()  # Read all channels
            image = image.transpose(1, 2, 0)  # Transpose to (height, width, channels)
            image_width = raster.width
            image_height = raster.height
    elif image_path.lower().endswith('.png'):
        image = Image.open(image_path)
        image_width, image_height = image.size
        image = np.array(image)
    else:
        raise ValueError("Unsupported file format")

    for top in range(0, image_height, tile_size):
        for left in range(0, image_width, tile_size):
            if top + tile_size > image_height:
                top = image_height - tile_size
            if left + tile_size > image_width:
                left = image_width - tile_size
            right = left + tile_size
            bottom = top + tile_size
            tile = image[top:bottom, left:right]

            if image_path.lower().endswith('.tif'):
                tile_path = os.path.join(output_folder, f"{os.path.basename(image_path).split('.')[0].split('_sat')[0]}_{int(np.ceil(top / tile_size))}_{int(np.ceil(left / tile_size))}_sat.tif")
                with rasterio.open(
                    tile_path,
                    'w',
                    driver='GTiff',
                    height=tile.shape[0],
                    width=tile.shape[1],
                    count=tile.shape[2],
                    dtype=tile.dtype
                ) as dst:
                    for i in range(tile.shape[2]):
                        dst.write(tile[:, :, i], i + 1)
            elif image_path.lower().endswith('.png'):
                tile_image = Image.fromarray(tile)
                tile_image.save(os.path.join(output_folder, f"{os.path.basename(image_path).split('.')[0].split('_mask')[0]}_{int(np.ceil(top / tile_size))}_{int(np.ceil(left / tile_size))}_mask.png"))

def cut_images_in_folder(input_folder, output_folder, tile_size=128):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        image_path = os.path.join(input_folder, filename)
        if filename.lower().endswith('.tif') or filename.lower().endswith('.png'):
            cut_image(image_path, output_folder, tile_size)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process satellite images.')
    parser.add_argument('--mode', type=str, choices=['image', 'folder'], required=True, help='Mode to process: image (tif image) or folder')
    parser.add_argument('--input', type=str, help='Input file or folder path')
    parser.add_argument('--output', type=str, help='Output folder path')
    parser.add_argument('--rotate', action='store_true', help='Rotate images', default=False)
    parser.add_argument('--tile_size', type=int, default=64, help='Tile size for cutting images')
    args = parser.parse_args()

    output_folder = args.output
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    tile_size = args.tile_size
    input_folder = ''

    if args.mode == 'image':
        input_image = args.input
        mask_image = input_image.replace('_sat.tif', '_mask.png')
        base_name = os.path.basename(input_image).split('_sat.')[0]
        input_folder = base_name + '_input'
        print(input_folder)
        os.makedirs(input_folder, exist_ok=True)
        normalize_image(mask_image, input_folder)
        shutil.copy(input_image, input_folder)

    elif args.mode == 'folder':
        input_folder = args.input
        normalize_images_in_folder(input_folder)

    if args.rotate:
        angle = 45
        rotate_images_in_folder(input_folder)

    cut_folder = input_folder + '_cut'
    cut_images_in_folder(input_folder, cut_folder, tile_size)

    max_black_pixel_rate = 0.3
    top_images = find_images_below_black_pixel_rate(cut_folder, max_black_pixel_rate)
    filtered_folder = cut_folder + '_low_black_pixel'
    save_results_to_file(top_images, output_file=f'{filtered_folder}.txt')
    copy_images_to_folder(top_images, cut_folder, filtered_folder)

    split_folder = filtered_folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_pattern = '*_sat.tif'

    # Find all files matching the pattern
    files = find_files_with_pattern(split_folder, file_pattern)
    print(f"Found {len(files)} files.")

    # Split the data into train, val, and test sets
    train_files, val_files, test_files = split_data(files, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1)
    print(f"Train files: {len(train_files)}, Validation files: {len(val_files)}, Test files: {len(test_files)}")

    # Define the destination directories
    train_folder = os.path.join(output_folder, 'train')
    val_folder = os.path.join(output_folder, 'val')
    test_folder = os.path.join(output_folder, 'test')

    # Copy the files and their corresponding masks to the respective directories
    copy_files_with_masks(train_files, train_folder, split_folder)
    copy_files_with_masks(val_files, val_folder, split_folder)
    copy_files_with_masks(test_files, test_folder, split_folder)

    print("Data split and copied successfully.")
