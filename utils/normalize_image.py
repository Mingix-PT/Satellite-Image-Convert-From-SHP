from PIL import Image
import numpy as np
import os

def normalize_image(input_folder, output_folder=None):
  # Iterate over all files in the input folder
  for root, _, files in os.walk(input_folder):
    for image_filename in files:
      # Construct the full image path
      image_path = os.path.join(root, image_filename)
      # print(f"Processing {image_path}")
      # Skip files that do not end with .png
      if not image_filename.lower().endswith('_mask.png'):
        continue
      # Open the image
      image = Image.open(image_path)
      # Convert the image to RGB if it is not already
      if image.mode != 'RGB':
        image = image.convert('RGB')

      # Convert the image to a numpy array
      image_array = np.array(image)
      # print(f"{image_filename}: {image_array.shape}")  # Print the shape of the image

      # Apply thresholding
      image_array = np.where(image_array > 128, 255, 0).astype(np.uint8)

      # Save the image
      new_image = Image.fromarray(image_array)
      if output_folder is None:
        output_folder = input_folder
      os.makedirs(output_folder, exist_ok=True)
      new_image.save(image_path)

# Example usage
normalize_image('gg_earth_32_dataset')
