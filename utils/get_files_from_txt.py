import os
import shutil

# Define paths
source_folder = 'cut_dataset'
target_folder = 'high_water_filtered_cutdown'

# Ensure the target folder exists
os.makedirs(target_folder, exist_ok=True)

# Read prefixes from high_water.txt
with open('high_water_filtered.txt', 'r') as file:
    files = file.readlines()

    # Remove the newline character
    files = [file.strip() for file in files]

subfolders = os.listdir(source_folder)

# Copy files to the target folder
for file in files:
    for subfolder in subfolders:
        mask_file = os.path.join(source_folder, subfolder, file + '_mask.png')
        sat_file = os.path.join(source_folder, subfolder, file + '_sat.tif')

        if not os.path.exists(mask_file) or not os.path.exists(sat_file):
            continue

        target_mask_file = os.path.join(target_folder, os.path.basename(file) + '_mask.png')
        target_sat_file = os.path.join(target_folder, os.path.basename(file) + '_sat.tif')

        shutil.copy(mask_file, target_mask_file)
        shutil.copy(sat_file, target_sat_file)
