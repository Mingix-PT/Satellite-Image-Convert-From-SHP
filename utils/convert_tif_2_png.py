import os
import numpy as np
import rasterio
from rasterio.plot import reshape_as_image
from PIL import Image

input_dir = 'high_black_pixel_images'
output_dir = input_dir

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Iterate over all files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.tif'):
        input_path = os.path.join(input_dir, filename)

        # Read the .tif file
        with rasterio.open(input_path) as src:
            # Read the first 3 channels
            image = src.read([1, 2, 3])
            image = np.nan_to_num(image) / (2**12 - 1) * 255  # Normalize and scale to 0-255
            image = reshape_as_image(image).astype(np.uint8)  # Reshape and convert to uint8

            # Convert to a PIL image
            img = Image.fromarray(image)

            # Save as .png
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.png")
            img.save(output_path)

print("Conversion completed.")
