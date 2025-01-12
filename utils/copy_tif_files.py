import os
import shutil

# Define the directories
source_dir = 'normalized_hoang_hoa_images'
target_dir = 'final_dataset'

# Get all files in the source directory
for filename in os.listdir(source_dir):
  if filename.endswith('_mask.png'):
    # Remove the '_mask.png' part to get the base name
    base_name = filename.replace('_mask.png', '')

    # Construct the corresponding _sat.tif filename
    sat_filename = f"{base_name}_sat.tif"

    # Check if the _sat.tif file exists in the target directory
    sat_file_path = os.path.join(target_dir, sat_filename)
    if os.path.exists(sat_file_path):
      # Copy the _sat.tif file to the source directory
      shutil.copy(sat_file_path, source_dir)
      print(f"Copied {sat_filename} to {source_dir}")
