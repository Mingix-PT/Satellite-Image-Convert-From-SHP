import os

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

folder_path = 'cut_dataset'
folder = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
for f in folder:
  file_count = count_files_in_folder(os.path.join(folder_path, f))
  print(f"Number of files in '{f}': {file_count}")
