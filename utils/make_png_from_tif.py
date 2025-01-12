import os
import numpy as np
import rasterio
from rasterio.plot import reshape_as_image
from PIL import Image

def convert_tif_to_png(input_dir, output_dir=None):
    if output_dir is None:
        output_dir = input_dir + '_png'

    if not os.path.exists(input_dir):
        raise ValueError(f"Input directory '{input_dir}' does not exist")

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all .tif files in the input directory
    tif_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.tif')]

    # Process each .tif file
    for tif_file in tif_files:
        with rasterio.open(tif_file) as src:
            # Read the first 3 channels
            count = src.count
            print(f"Number of bands: {count}")
            img = []
            for i in range(4, 1, -1):
                print(f"Reading band {i}...")
                img_band_i = src.read([i])
                max_power_2 = 2 ** 12 - 1
                # img_band_i = img_band_i / (max_power_2)
                img_band_i = (img_band_i * 355.0).astype('uint8')
                max_img = img_band_i.max()
                min_img = img_band_i.min()
                print(f"Band {i}: min={min_img}, max={max_img}")
                img.append(img_band_i)
            # Reshape the image to (height, width, channels)
            img = np.stack(img, axis=-1)[0]
            # Convert to a PIL image
            img = Image.fromarray((img * 1.5).astype('uint8'))
            # Save as .png
            output_file = os.path.join(output_dir, os.path.basename(tif_file).replace('.tif', '.png'))
            img.save(output_file)

    print("Conversion completed.")

# Example usage
if __name__ == '__main__':
    convert_tif_to_png('gg_earth_25km2_13band_resized_dataset/test', 'gg_earth_25km2_13band_resized_dataset_test_png')
