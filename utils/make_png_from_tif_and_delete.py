import os
import numpy as np
import rasterio
from rasterio.plot import reshape_as_image
from PIL import Image

def convert_tif_to_png(input_dir, delete_tif=False):
    output_dir = input_dir

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
            img = []
            for i in range(1, 4):
                img_band_i = src.read([i])
                max_img = img_band_i.max()
                img_band_i = img_band_i / (max_img)
                img_band_i = (img_band_i * 255).astype('uint8')
                img.append(img_band_i)
            # Reshape the image to (height, width, channels)
            img = np.stack(img, axis=-1)[0]
            # Convert to a PIL image
            img = Image.fromarray(img)
            # Save as .png
            output_file = os.path.join(output_dir, os.path.basename(tif_file).replace('.tif', '.png'))
            img.save(output_file)

        if delete_tif:
            os.remove(tif_file)

    print("Conversion completed.")

# Example usage
if __name__ == '__main__':
    convert_tif_to_png('high_water', delete_tif=True)
