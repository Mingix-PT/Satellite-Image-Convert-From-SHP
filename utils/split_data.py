import os
import shutil
import glob
from sklearn.model_selection import train_test_split

def find_files_with_pattern(directory, pattern):
    search_pattern = os.path.join(directory, '**', pattern)
    matching_files = glob.glob(search_pattern, recursive=True)
    return matching_files

def split_data(files, train_ratio=0.6, val_ratio=0.3, test_ratio=0.1):
    train_files, temp_files = train_test_split(files, test_size=(1 - train_ratio))
    val_files, test_files = train_test_split(temp_files, test_size=(test_ratio / (val_ratio + test_ratio)))
    return train_files, val_files, test_files

def copy_files_with_masks(files, destination_folder, source_directory):
    os.makedirs(destination_folder, exist_ok=True)
    for file in files:
        shutil.copy(file, destination_folder)
        # Find and copy the corresponding mask file
        base_name = os.path.basename(file).replace('_sat.tif', '')
        mask_file = os.path.join(source_directory, f'{base_name}_mask.png')
        if os.path.exists(mask_file):
            shutil.copy(mask_file, destination_folder)
        else:
            print(f"Mask file not found for {file}")

def move_files_with_masks(files, destination_folder, source_directory):
    os.makedirs(destination_folder, exist_ok=True)
    for file in files:
        shutil.copy(file, destination_folder)
        # Find and copy the corresponding mask file
        base_name = os.path.basename(file).replace('_sat.tif', '')
        mask_file = os.path.join(source_directory, f'{base_name}_mask.png')
        if os.path.exists(mask_file):
            shutil.copy(mask_file, destination_folder)
        else:
            print(f"Mask file not found for {file}")

if __name__ == "__main__":
    # Define the source directory and file pattern
    source_directory = 'new_13bands_dataset_100125'
    destination_directory = source_directory + '_splitted'
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    file_pattern = '*_sat.tif'

    # Find all files matching the pattern
    files = find_files_with_pattern(source_directory, file_pattern)
    print(f"Found {len(files)} files.")

    # Split the data into train, val, and test sets
    train_files, val_files, test_files = split_data(files, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1)
    print(f"Train files: {len(train_files)}, Validation files: {len(val_files)}, Test files: {len(test_files)}")

    # Define the destination directories
    train_folder = os.path.join(destination_directory, 'train')
    val_folder = os.path.join(destination_directory, 'val')
    test_folder = os.path.join(destination_directory, 'test')

    # Copy the files and their corresponding masks to the respective directories
    copy_files_with_masks(train_files, train_folder, source_directory)
    copy_files_with_masks(val_files, val_folder, source_directory)
    copy_files_with_masks(test_files, test_folder, source_directory)

    print("Data split and copied successfully.")
