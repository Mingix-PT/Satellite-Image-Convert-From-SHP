import os
import shutil

def find_excluded_files(source_dir, target_dir, prefix):
  source_files = set(f for f in os.listdir(source_dir) if f.startswith(prefix))
  print(f"Found {len(source_files)} files in source directory")
  target_files = set(os.listdir(target_dir))
  print(f"Found {len(target_files)} files in target directory")

  excluded_files = source_files - target_files
  return excluded_files

source_directory = 'hoang_hoa_dataset_filtered'
target_directory = 'final_dataset_filtered'
excluded_directory = 'hoang_hoa_excluded'
file_prefix = 'HoangHoa'

excluded_files = find_excluded_files(source_directory, target_directory, file_prefix)

# Ensure the excluded directory exists
os.makedirs(excluded_directory, exist_ok=True)

print(f"Found {len(excluded_files)} files to exclude")

for file in excluded_files:
  source_file_path = os.path.join(source_directory, file)
  destination_file_path = os.path.join(excluded_directory, file)
  shutil.copy2(source_file_path, destination_file_path)
  # print(f"Copied {file} to {excluded_directory}")
