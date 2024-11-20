import os
from PIL import Image
import numpy as np
import shutil
import argparse

def calculate_color_pixel_rate(image_path, color=[0, 0, 0]):
    image = Image.open(image_path).convert('RGBA')  # Ensure the image has 4 channels
    image_np = np.array(image)
    total_pixels = image_np.shape[0] * image_np.shape[1]
    color_pixels = np.sum(np.all(image_np[:, :, :3] == color, axis=-1))  # Ignore the alpha channel for comparison
    return color_pixels / total_pixels

def find_images_between_color_pixel_rate(input, color, min_color_pixel_rate, max_color_pixel_rate):
    image_color_pixel_rates = []

    for filename in os.listdir(input):
        if filename.endswith('.png'):
            image_path = os.path.join(input, filename)
            color_pixel_rate = calculate_color_pixel_rate(image_path, color)
            if color_pixel_rate >= min_color_pixel_rate and color_pixel_rate <= max_color_pixel_rate:
                image_color_pixel_rates.append((filename, color_pixel_rate))

    return image_color_pixel_rates

def save_results_to_file(top_images, output_file):
    top_images.sort()
    with open(output_file, 'w') as f:
        for image, rate in top_images:
            f.write(f"{image.replace('_mask.png', '')}\n")

    print(f"The results have been saved to {output_file}")

if __name__ == '__main__':
    class_to_color = {
        'unidentifiable': [0, 0, 0],
        'rice_field': [255, 0, 0],
        'forest': [0, 255, 0],
        'water': [0, 255, 255],
        'residential': [255, 255, 0],
    }

    parser = argparse.ArgumentParser(description='Filter images based on color pixel rate.')
    parser.add_argument('--input', type=str, help='input folder containing images')
    parser.add_argument('--output', type=str, default='filtered_images.txt', help='output file to save the results (default: filtered_images.txt)')
    parser.add_argument('--class_name', type=str, default='unidentifiable', help='Class to filter by (default: unidentifiable)')
    parser.add_argument('--maximum_rate', type=float, default=1.0, help='Maximum color pixel rate (default: 1.0)')
    parser.add_argument('--minimum_rate', type=float, default=0.0, help='Minimum color pixel rate (default: 0.0)')
    args = parser.parse_args()

    input = args.input
    class_name = args.class_name
    maximum_rate = args.maximum_rate
    minimum_rate = args.minimum_rate
    output = args.output

    color = class_to_color[class_name]

    if maximum_rate < minimum_rate:
        raise ValueError("Maximum rate must be greater than or equal to minimum rate")

    if maximum_rate > 1.0 or maximum_rate < 0.0:
        raise ValueError("Maximum rate must be between 0.0 and 1.0")

    if minimum_rate > 1.0 or minimum_rate < 0.0:
        raise ValueError("Minimum rate must be between 0.0 and 1.0")

    filtered_images = find_images_between_color_pixel_rate(input, color, minimum_rate, maximum_rate)
    save_results_to_file(filtered_images, output)
