import os
import numpy as np
import rasterio
from rasterio.plot import reshape_as_image
import cv2
import shutil

def rotate_image(img, angle):
    # Get image dimensions
    h, w = img.shape[:2]
    # print(f"Original image shape: {img.shape}")
    center = (w // 2, h // 2)
    radians = np.deg2rad(angle)
    # print(f"Rotation angle in radians: {radians}")

    # Calculate new dimensions
    new_w = int(abs(w * np.cos(radians)) + abs(h * np.sin(radians)))
    new_h = int(abs(h * np.cos(radians)) + abs(w * np.sin(radians)))
    # print(f"New image dimensions: {new_w} x {new_h}")

    # Adjust the rotation matrix to take into account the translation
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    M[0, 2] += (new_w - w) / 2
    M[1, 2] += (new_h - h) / 2

    # Perform the rotation with the new bounding dimensions
    rotated_img = cv2.warpAffine(img, M, (new_w, new_h))
    return rotated_img, new_w, new_h

def rotate_images(input_folder_path, output_folder_path, angle):
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    for filename in os.listdir(input_folder_path):
        if filename.endswith('.tif'):
            image_path = os.path.join(input_folder_path, filename)
            try:
                with rasterio.open(image_path) as src:
                    img = src.read()
                    img = reshape_as_image(img)  # Convert to (height, width, channels)

                # Use the function in the main code
                rotated_img, new_w, new_h = rotate_image(img, angle)
                # print(f"Rotated image shape: {rotated_img.shape}")

                # Save the rotated image using rasterio
                save_name = filename.replace('_sat.tif', '_rotated_sat.tif')
                output_image_path = os.path.join(output_folder_path, save_name)
                with rasterio.open(output_image_path, 'w', driver='GTiff', height=new_h, width=new_w, count=img.shape[2], dtype=img.dtype) as dst:
                    for i in range(img.shape[2]):
                        dst.write(rotated_img[:, :, i], i + 1)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
        elif filename.endswith('.png'):
            image_path = os.path.join(input_folder_path, filename)
            try:
                img = cv2.imread(image_path)

                # Use the function in the main code
                rotated_img, new_w, new_h = rotate_image(img, angle)
                print(f"Rotated image shape: {rotated_img.shape}")

                # Save the rotated image using OpenCV
                save_name = filename.replace('_mask.png', '_rotated_mask.png')
                output_image_path = os.path.join(output_folder_path, save_name)
                cv2.imwrite(output_image_path, rotated_img)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    input_folder_path = 'test_sentinel_image_resized'
    output_folder_path = input_folder_path + "_rotated"
    angle = 45
    rotate_images(input_folder_path, output_folder_path, angle)
    for file in os.listdir(input_folder_path):
        src_file = os.path.join(input_folder_path, file)
        dst_file = os.path.join(output_folder_path, file)
        shutil.copy(src_file, dst_file)
