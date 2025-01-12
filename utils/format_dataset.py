import os
import shutil

def create_directories(root):
    os.makedirs(os.path.join(root, 'images', 'test'), exist_ok=True)
    os.makedirs(os.path.join(root, 'images', 'train'), exist_ok=True)
    os.makedirs(os.path.join(root, 'images', 'val'), exist_ok=True)
    os.makedirs(os.path.join(root, 'masks', 'test'), exist_ok=True)
    os.makedirs(os.path.join(root, 'masks', 'train'), exist_ok=True)
    os.makedirs(os.path.join(root, 'masks', 'val'), exist_ok=True)
    os.makedirs(os.path.join(root, 'splits'), exist_ok=True)

def move_files_and_create_splits(root, target_root, split):
    images_dir = os.path.join(target_root, 'images', split)
    masks_dir = os.path.join(target_root, 'masks', split)
    split_file = os.path.join(target_root, 'splits', f'{split}.txt')

    with open(split_file, 'w') as f:
        split_path = os.path.join(root, split)
        for file_name in os.listdir(split_path):
            if file_name.endswith('_sat.tif'):
                base_name = file_name.replace('_sat.tif', '')
                shutil.copy(os.path.join(split_path, file_name), os.path.join(images_dir, file_name))
                mask_name = base_name + '_mask.png'
                shutil.copy(os.path.join(split_path, mask_name), os.path.join(masks_dir, mask_name))
                f.write(base_name + '\n')

if __name__ == '__main__':
    root = 'gg_earth_25km2_13band_resized_dataset'
    target_root = '13band_formatted_dataset'
    create_directories(target_root)
    for split in ['test', 'train', 'val']:
        move_files_and_create_splits(root, target_root, split)
