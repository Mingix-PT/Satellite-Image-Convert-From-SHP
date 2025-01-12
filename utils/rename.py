import os

folder_path = 'new_13bands_dataset_100125'

for filename in os.listdir(folder_path):
        new_filename = filename.replace('.tif', '_sat.tif')
        os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))
