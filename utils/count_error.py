import os

def list_unique_tif_files(source_dir, compare_dir):
    # List all TIF files in both directories
    source_tif_files = {f for f in os.listdir(source_dir) if f.endswith('.tif')}
    compare_tif_files = {f for f in os.listdir(compare_dir) if f.endswith('.tif')}

    # Find TIF files that are in source_dir but not in compare_dir
    unique_tif_files = source_tif_files - compare_tif_files

    return unique_tif_files

# Define the directories
source_dir = 'final_dataset'
compare_dir = 'final_dataset_filtered'

# Get the list of unique TIF files
unique_tif_files = list_unique_tif_files(source_dir, compare_dir)

# Save the unique TIF files to a text file
output_file = 'unique_tif_files.txt'
with open(output_file, 'w') as f:
    for tif_file in unique_tif_files:
        f.write(f"{tif_file}\n")

print(f"The unique TIF files have been saved to {output_file}")
