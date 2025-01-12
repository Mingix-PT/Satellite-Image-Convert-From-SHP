import os

def delete_files_with_patterns(directory, patterns):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(pattern in file for pattern in patterns):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

# Specify the directory and patterns
directory = 'data'  # Change this to your target directory
patterns = ['evi', 'ndmi', 'NDVI', 'unidentifiable']

# Delete files with specified patterns
delete_files_with_patterns(directory, patterns)
