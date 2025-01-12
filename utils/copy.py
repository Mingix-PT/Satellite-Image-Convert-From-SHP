import os
import shutil

source_dir = '.'
destination_dir = 'flow'

if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

for file_name in os.listdir(source_dir):
    if file_name.endswith('.py'):
        full_file_name = os.path.join(source_dir, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, destination_dir)
