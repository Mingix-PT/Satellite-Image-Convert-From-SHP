import os
import glob

def delete_tif_files(folder_path):
    tif_files = glob.glob(os.path.join(folder_path, '*.tif'))
    for tif_file in tif_files:
        try:
            os.remove(tif_file)
            # print(f"Deleted: {tif_file}")
        except Exception as e:
            print(f"Error deleting {tif_file}: {e}")

if __name__ == "__main__":
    folder_path = 'high_water'  # Change this to your folder path
    delete_tif_files(folder_path)
