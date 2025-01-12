import os
from PIL import Image
import numpy as np
import shutil
import glob
from sklearn.model_selection import train_test_split

green_color = [0, 255, 0]

def calculate_black_pixel_rate(image_path):
    image = Image.open(image_path).convert('RGBA')  # Ensure the image has 4 channels
    image_np = np.array(image)
    total_pixels = image_np.shape[0] * image_np.shape[1]
    black_pixels = np.sum(np.all(image_np[:, :, :3] == [0, 0, 0], axis=-1))  # Ignore the alpha channel for comparison
    return black_pixels / total_pixels

def calculate_color_pixel_rate(image_path, color=[0, 0, 0]):
    image = Image.open(image_path).convert('RGBA')  # Ensure the image has 4 channels
    image_np = np.array(image)
    total_pixels = image_np.shape[0] * image_np.shape[1]
    color_pixels = np.sum(np.all(image_np[:, :, :3] == color, axis=-1))  # Ignore the alpha channel for comparison
    return color_pixels / total_pixels

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
    print(f"Found {len(image_black_pixel_rates)} images with black pixel rate <= {max_black_pixel_rate}")

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

def copy_images_to_folder(top_images, source_directory, destination_directory):
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    for image, _ in top_images:
        tif_image = image.replace('_mask.png', '_sat.tif')
        source_path = os.path.join(source_directory, image)
        destination_path = os.path.join(destination_directory,
                                        image.replace('_mask.png', '_rotated_mask.png')
                                             )

        tif_source_path = os.path.join(source_directory, tif_image)
        tif_destination_path = os.path.join(destination_directory,
                                            tif_image.replace('_sat.tif', '_rotated_sat.tif'))

        shutil.move(source_path, destination_path)
        shutil.move(tif_source_path, tif_destination_path)

    print(f"Copied {len(top_images)} images to {destination_directory}")

def find_images_below_color_pixel_rate(directory, color, color_pixel_rate):
    image_color_pixel_rates = []

    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            if color == green_color and filename.startswith('QuanSon'):
                print(f'Skipping {filename}...')
                continue
            image_path = os.path.join(directory, filename)
            color_pixel_rate = calculate_color_pixel_rate(image_path, color)
            if color_pixel_rate <= color_pixel_rate:
                image_color_pixel_rates.append((filename, color_pixel_rate))

    return image_color_pixel_rates

if __name__ == '__main__':
    directory = 'final_dataset_new_rotated_cut'
    output_folder = directory + '_low_black_pixel'
    max_black_pixel_rate = 0.3
    top_images = find_images_below_black_pixel_rate(directory, max_black_pixel_rate)
    save_results_to_file(top_images, output_file=f'{output_folder}.txt')
    copy_images_to_folder(top_images, directory, output_folder)

    # directory = 'full_complete_dataset_renamed'
    # max_color_pixel_rate = 0.3
    # top_images = find_images_below_color_pixel_rate(directory, green_color, max_color_pixel_rate)
    # output_folder = 'low_green_pixel_images'
    # save_results_to_file(top_images, output_file=f'{output_folder}.txt')
