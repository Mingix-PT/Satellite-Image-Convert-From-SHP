import os

def delete_satellite_images(folder_path):
  for filename in os.listdir(folder_path):
    if filename.endswith('_sat.png'):
      file_path = os.path.join(folder_path, filename)
      os.remove(file_path)
      print(f"Deleted: {file_path}")

# Example usage
delete_satellite_images('augment_images')
