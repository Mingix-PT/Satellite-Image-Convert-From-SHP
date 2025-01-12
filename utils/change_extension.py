import os

def change_extension(folder_path, old_new_exts):
    for filename in os.listdir(folder_path):
        for old_ext, new_ext in old_new_exts.items():
            if filename.endswith(old_ext):
                base = os.path.splitext(filename)[0]
                new_name = base.replace(old_ext, new_ext)
                os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_name))
                break  # Exit the loop once a match is found

if __name__ == "__main__":
    folder_path = 'sentinel/25km/sentinel_dataset_rotated'  # Replace with your folder path
    folder = ['train', 'val', 'test']
    old_new_exts = {
        '_sat.tif': '_rotated_sat.tif',
        '_mask.png': '_rotated_mask.png'
    }
    for f in folder:
        change_extension(os.path.join(folder_path, f), old_new_exts)
