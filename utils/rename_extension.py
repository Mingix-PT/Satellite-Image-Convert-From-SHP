import os

folder_path = 'new_hoang_hoa_excluded'

for filename in os.listdir(folder_path):
  if filename.endswith('_sat.png'):
    new_filename = filename.replace('_sat.png', '_mask.png')
    os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))

print("Renaming completed.")
