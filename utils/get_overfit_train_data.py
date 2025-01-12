import os
import shutil

# Define the source and destination directories
source_dir = 'final_dataset'
destination_dir = 'train_overfit'

# Ensure the destination directory exists
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

# Read the file names from the text file
with open('least_black_pixel_images.txt', 'r') as file:
    content = file.read()

# Process the content to get the file names
file_names = [name.strip().strip("'") for name in content.split(',') if name.strip()]

# Append the suffixes and copy the files
for name in file_names:
    image_file = f"{name}_sat.tif"
    mask_file = f"{name}_mask.png"

    # Define the full paths for the source and destination files
    image_src_path = os.path.join(source_dir, image_file)
    mask_src_path = os.path.join(source_dir, mask_file)
    image_dest_path = os.path.join(destination_dir, image_file)
    mask_dest_path = os.path.join(destination_dir, mask_file)

    # Copy the image file if it exists
    if os.path.exists(image_src_path):
        shutil.copy(image_src_path, image_dest_path)
    else:
        print(f"Image file {image_src_path} does not exist.")

    # Copy the mask file if it exists
    if os.path.exists(mask_src_path):
        shutil.copy(mask_src_path, mask_dest_path)
    else:
        print(f"Mask file {mask_src_path} does not exist.")

print("Files have been copied to the train_overfit folder.")
