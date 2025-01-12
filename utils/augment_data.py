import os
import shutil
import numpy as np
import random
import torch
from torchvision.transforms.functional import hflip, vflip, rotate
import rasterio
from PIL import Image, ImageEnhance
import argparse
import glob
from sklearn.model_selection import train_test_split
from collections import defaultdict

color_to_class = {
  (0, 0, 0): 'unidentifiable',
  (0, 0, 255): 'bamboo',
  (0, 255, 0): 'forest',
  (255, 0, 0): 'rice_field',
  (0, 255, 255): 'water',
  (255, 255, 0): 'residential',
}

green_color = [0, 255, 0]

def copy_files(source_dir, destination_dir, exception=None):
  for filename in os.listdir(source_dir):
    source_file = os.path.join(source_dir, filename)
    destination_file = os.path.join(destination_dir, filename)

    if not os.path.exists(destination_file) and (exception is None or exception not in filename):
      shutil.copy2(source_file, destination_file)

def calculate_color_pixel_rate(image_path, color=[0, 0, 0]):
    image = Image.open(image_path).convert('RGBA')  # Ensure the image has 4 channels
    image_np = np.array(image)
    total_pixels = image_np.shape[0] * image_np.shape[1]
    color_pixels = np.sum(np.all(image_np[:, :, :3] == color, axis=-1))  # Ignore the alpha channel for comparison
    return color_pixels / total_pixels

def find_images_below_color_pixel_rate(directory, color, color_pixel_rate):
    low_rate_color_images = []

    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            # if color == green_color and filename.startswith('QuanSon'):
                # print(f'Skipping {filename}...')
                # continue
            image_path = os.path.join(directory, filename)
            color_pixel_rate = calculate_color_pixel_rate(image_path, color)
            if color_pixel_rate <= color_pixel_rate:
                low_rate_color_images.append(filename.replace('_mask.png', ''))

    return low_rate_color_images

def save_results_to_file(top_images, output_file='low_black_pixel_images.txt'):
    top_images.sort()
    with open(output_file, 'w') as f:
        for image, rate in top_images:
            f.write(f"{image.replace('_mask.png', '')}\n")

    print(f"The results have been saved to {output_file}")

def read_file_paths(file_path, folder_path):
  """
  Reads each line of a text file and returns a list of file paths.

  :param file_path: Path to the text file containing file paths.
  :return: List of file paths.
  """
  file_paths = []
  with open(file_path, 'r') as file:
    for line in file:
      file_path = os.path.join(folder_path, line.strip())
      file_paths.append(file_path)
  print(f'Number of file paths read: {len(file_paths)}')
  return file_paths

def custom_adjust_brightness(image, factor=1.5):
    if isinstance(image, torch.Tensor):
        return image * factor
    else:
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

def add_gaussian_noise(image: torch.Tensor, mean=0, std=0.1):
  noise = np.random.normal(mean, std, image.shape)
  noisy_image = image + noise
  return noisy_image

def augment_images(file_paths, augment_folder, num_augmentations=10, save_pngs=False):
  for i, file_path in enumerate(file_paths):
    # if (i == 5):
    #   break
    mask_path = file_path + '_mask.png'
    tif_path = file_path + '_sat.tif'
    # Open mask image with PIL
    mask_image = Image.open(mask_path).convert('RGB')
    tif_image = None

    # Open tif image with rasterio
    with rasterio.open(tif_path) as raster:
      # Read 5 channels
      tif_image = raster.read()  # Read all channels
      tif_image = tif_image.transpose(1, 2, 0)  # Transpose to (height, width, channels)
      tif_image = np.nan_to_num(tif_image)
      tif_image = torch.from_numpy(tif_image).permute(2, 0, 1)

    # Apply augmentations
    for i in range(num_augmentations):
      augment = {
        'hflip': False,
        'vflip': False,
        'rotate': 0,
        'brightness': False,
        'noise': False
      }
      augmented_mask_image = mask_image.copy()
      augmented_tif_image = tif_image.clone()

      # Randomly flip the image horizontally
      if random.random() > 0.5:
        augment['hflip'] = True
        augmented_mask_image = hflip(augmented_mask_image)
        augmented_tif_image = hflip(augmented_tif_image)

      # Randomly flip the image vertically
      if random.random() > 0.5:
        augment['vflip'] = True
        augmented_mask_image = vflip(augmented_mask_image)
        augmented_tif_image = vflip(augmented_tif_image)

      # Randomly rotate the image by a degree between -30 and 30
      angle = random.choice([0, 90, 1800, 270])
      if angle != 0:
        augment['rotate'] = angle
        augmented_mask_image = rotate(augmented_mask_image, angle)
        augmented_tif_image = rotate(augmented_tif_image, angle)

      # Randomly adjust the brightness of the image
      if random.random() > 0.5:
        augment['brightness'] = True
        brightness_factor = random.uniform(0.5, 1.5)
        augmented_tif_image = custom_adjust_brightness(augmented_tif_image, brightness_factor)

      # Add Gaussian noise to the image
      if random.random() > 0.5:
        augment['noise'] = True
        augmented_tif_image = add_gaussian_noise(augmented_tif_image)

      # Save the augmented images
      base_name = os.path.basename(file_path)

      mask_output_path = os.path.join(augment_folder, f'{base_name}_{i}_mask.png')
      tif_output_path = os.path.join(augment_folder, f'{base_name}_{i}_sat.tif')

      # Save augmented mask image using PIL
      augmented_mask_image = Image.fromarray(np.array(augmented_mask_image.convert('RGB')))
      augmented_mask_image.save(mask_output_path)

      # Save augmented tif image using rasterio
      augmented_tif_image = augmented_tif_image.permute(1, 2, 0).numpy()
      with rasterio.open(
        tif_output_path,
        'w',
        driver='GTiff',
        height=augmented_tif_image.shape[0],
        width=augmented_tif_image.shape[1],
        count=augmented_tif_image.shape[2],
        dtype=augmented_tif_image.dtype
      ) as dst:
        for j in range(augmented_tif_image.shape[2]):
          dst.write(augmented_tif_image[:, :, j], j + 1)

      # Save augmented tif image png using PIL if save_pngs is True
      if save_pngs:
        augmented_tif_image_png = augmented_tif_image[:, :, :3] / (2**13 - 1)
        augmented_tif_image_png = Image.fromarray((augmented_tif_image_png * 255).astype(np.uint8))
        augmented_tif_image_png.save(tif_output_path.replace('.tif', '.png'))

def find_files_with_pattern(directory, pattern):
    search_pattern = os.path.join(directory, '**', pattern)
    matching_files = glob.glob(search_pattern, recursive=True)
    return matching_files

def split_data(files, train_ratio=0.6, val_ratio=0.3, test_ratio=0.1):
    train_files, temp_files = train_test_split(files, test_size=(1 - train_ratio))
    val_files, test_files = train_test_split(temp_files, test_size=(test_ratio / (val_ratio + test_ratio)))
    return train_files, val_files, test_files

def copy_files_with_masks(files, destination_folder, source_directory):
    os.makedirs(destination_folder, exist_ok=True)
    for file in files:
        shutil.move(file, destination_folder)
        # Find and copy the corresponding mask file
        base_name = os.path.basename(file).replace('_sat.tif', '')
        mask_file = os.path.join(source_directory, f'{base_name}_mask.png')
        if os.path.exists(mask_file):
            shutil.move(mask_file, destination_folder)
        else:
            print(f"Mask file not found for {file}")

def calculate_color_distribution(folder_path):
    color_count = defaultdict(int)
    total_pixels = 0

    # Iterate through all PNG files in the folder
    print(f"Nummber of files in folder: {len(os.listdir(folder_path))}")
    for filename in os.listdir(folder_path):
        if filename.endswith('.png'):
            image_path = os.path.join(folder_path, filename)
            image = Image.open(image_path).convert('RGB')
            pixels = np.array(image)

            # Reshape the image array to list all pixels in RGB format
            pixels = pixels.reshape(-1, 3)
            total_pixels += len(pixels)

            # Count each unique color
            for color in pixels:
                color_tuple = tuple(color)
                color_count[color_tuple] += 1

    # Calculate percentage distribution of each color
    color_distribution = {color: (count / total_pixels) for color, count in color_count.items()}

    # Sort colors by percentage for better readability
    sorted_color_distribution = dict(sorted(color_distribution.items(), key=lambda item: item[1], reverse=True))

    return sorted_color_distribution

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Augment satellite images.')
    parser.add_argument('source_folder', type=str, help='Directory containing the source images')
    parser.add_argument('--color_pixel_rate', type=float, default=0.3, help='Color pixel rate threshold')
    parser.add_argument('--color', type=int, nargs=3, default=[0, 255, 0], help='Color to check for')
    parser.add_argument('--num_augmentations', type=int, default=5, help='Number of augmentations per image')
    parser.add_argument('--split_folder', type=str, default=None, help='Split folder for augmented image dataset')
    args = parser.parse_args()

    source_folder = args.source_folder
    color_pixel_rate = 0.3
    color = green_color
    print(f'Finding images with color pixel rate below {color_pixel_rate}...')
    low_rate_color_images = find_images_below_color_pixel_rate(source_folder, color, color_pixel_rate)
    low_rate_color_images = [os.path.join(source_folder, image) for image in low_rate_color_images]

    augment_folder = source_folder + '_augmented'
    if not os.path.exists(augment_folder):
      os.makedirs(augment_folder)

    copy_files(source_folder, augment_folder)

    print('Augmenting images...')
    augment_images(low_rate_color_images, augment_folder, num_augmentations=args.num_augmentations)
    print('Images augmented successfully.')

    split_folder = args.split_folder if args.split_folder else source_folder + '_augmented_dataset'
    if not os.path.exists(split_folder):
      os.makedirs(split_folder)

    print('Splitting augmented images into train val test...')
    file_pattern = '*_sat.tif'
    files = find_files_with_pattern(augment_folder, file_pattern)
    train_files, val_files, test_files = split_data(files, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1)

    train_folder = os.path.join(split_folder, 'train')
    val_folder = os.path.join(split_folder, 'val')
    test_folder = os.path.join(split_folder, 'test')

    copy_files_with_masks(train_files, train_folder, augment_folder)
    copy_files_with_masks(val_files, val_folder, augment_folder)
    copy_files_with_masks(test_files, test_folder, augment_folder)
    print('Data split and copied successfully.')

    print("Calculating class distribution:")
    folder_paths = ['train', 'val', 'test']
    for folder_path in folder_paths:
        full_path = os.path.join(split_folder, folder_path)
        print(f"\nColor distribution for {folder_path}:")
        color_distribution = calculate_color_distribution(full_path)
        for color, percentage in color_distribution.items():
            if color in color_to_class:
                print(f"{color_to_class[color]}: {percentage:.4f}")
