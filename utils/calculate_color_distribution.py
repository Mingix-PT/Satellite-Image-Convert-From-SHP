from PIL import Image
import numpy as np
import os
from collections import defaultdict
import matplotlib.pyplot as plt

def calculate_color_distribution(folder_path):
    color_count = defaultdict(int)
    total_pixels = 0

    # Iterate through all PNG files in the folder
    tif_files = [f for f in os.listdir(folder_path) if f.endswith('.tif')]
    print(f"Number of files in folder: {len(tif_files)}")
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

color_to_class = {
  (0, 0, 0): 'unidentifiable',
  (0, 255, 0): 'forest',
  (255, 0, 0): 'rice_field',
  (0, 255, 255): 'water',
  (255, 255, 0): 'residential',
}

if __name__ == "__main__":
    folder_paths = ['train', 'val', 'test']
    base_folder = 'gg_earth_25km2_13band_resized_dataset'
    color_distribution = {
        'train': defaultdict(dict),
        'val': defaultdict(dict),
        'test': defaultdict(dict),
    }
    for folder_path in folder_paths:
        full_path = os.path.join(base_folder, folder_path)
        print(f"\nColor distribution for {folder_path}:")
        color_distribution[folder_path] = calculate_color_distribution(full_path)
        for color, percentage in color_distribution[folder_path].items():
            if color in color_to_class:
                print(f"'{color_to_class[color]}': {percentage:.4f},")
