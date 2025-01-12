import os
import shutil

def move_files_out_of_data_dirs(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'data' in dirnames:
            data_dir = os.path.join(dirpath, 'data')
            parent_dir = dirpath
            for filename in os.listdir(data_dir):
                file_path = os.path.join(data_dir, filename)
                shutil.move(file_path, parent_dir)
            os.rmdir(data_dir)

# Get the current directory
current_directory = os.getcwd()

# Iterate over each subdirectory in the current directory
for subdir in os.listdir(current_directory):
    subdir_path = os.path.join(current_directory, subdir)
    if os.path.isdir(subdir_path):
        move_files_out_of_data_dirs(subdir_path)
