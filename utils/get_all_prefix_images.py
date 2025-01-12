import os
import shutil

source_dir = 'final_dataset_new'
destination_dir = 'qs_complete_dataset'

def count_files_in_folder(folder_path, extension='.tif', start_name=None):
  try:
    files = os.listdir(folder_path)
    files = [f for f in files if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(extension)]
    if start_name:
      files = [f for f in files if f.startswith(start_name)]
    file_count = len(files)
    return file_count
  except Exception as e:
    print(f"An error occurred: {e}")
    return 0

if not os.path.exists(destination_dir):
  os.makedirs(destination_dir)

for filename in os.listdir(source_dir):
  if filename.startswith('QuanSon'):
    source_file = os.path.join(source_dir, filename)
    destination_file = os.path.join(destination_dir, filename)
    shutil.copy(source_file, destination_file)
    # print(f'Copied {filename} to {destination_dir}')

file_number = count_files_in_folder(destination_dir)
print(f'Copied {file_number} files from {source_dir} to {destination_dir}')
