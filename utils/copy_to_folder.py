import os
import shutil

source_dir = 'full_complete_dataset_renamed'
destination_dir = 'augment_images'

if not os.path.exists(destination_dir):
  os.makedirs(destination_dir)

for filename in os.listdir(source_dir):
  source_file = os.path.join(source_dir, filename)
  destination_file = os.path.join(destination_dir, filename)

  if not os.path.exists(destination_file):
    shutil.copy2(source_file, destination_file)
