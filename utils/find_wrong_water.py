import os
from PIL import Image
import numpy as np

def is_valid_image(image_path):
  image = Image.open(image_path)
  image_np = np.array(image)
  unique_colors = np.unique(image_np.reshape(-1, image_np.shape[2]), axis=0)
  valid_colors = [np.array([0, 255, 255]), np.array([0, 0, 0])]
  return all(any(np.array_equal(color, valid_color) for valid_color in valid_colors) for color in unique_colors)

def find_invalid_images(folder_path):
  invalid_images = []
  for root, _, files in os.walk(folder_path):
    for file in files:
      if file.lower().endswith('.png'):
        image_path = os.path.join(root, file)
        if not is_valid_image(image_path):
          invalid_images.append(os.path.basename(image_path))
  return invalid_images

if __name__ == "__main__":
  folder_path = 'final_dataset'
  invalid_images = find_invalid_images(folder_path)
  if invalid_images:
    print("Invalid images found:")
    for img in invalid_images:
      print(img)
    with open('invalid_images.txt', 'w') as f:
      for img in invalid_images:
        f.write(f"{img}\n")
  else:
    print("All images are valid.")
