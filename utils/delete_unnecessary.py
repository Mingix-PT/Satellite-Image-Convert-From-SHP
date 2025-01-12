import os

# Directory containing the files
directory = r'D:\Satellite Images\final_dataset_new'

# Loop through all files in the directory
for filename in os.listdir(directory):
    # Check if 'rotated' is in the filename
    if 'rotated' in filename:
        # Construct full file path
        file_path = os.path.join(directory, filename)
        # Delete the file
        os.remove(file_path)
        print(f"Deleted: {file_path}")
