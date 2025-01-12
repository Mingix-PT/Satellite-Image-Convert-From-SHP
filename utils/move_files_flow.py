import os
import shutil

# Thư mục gốc chứa các thư mục MONTH_01 đến MONTH_12
root_folder = 'Huy_missing_files'

# Thư mục đích chứa tất cả các file
destination_folder = 'Huy_missing_files_folder'

# Tạo thư mục đích nếu nó chưa tồn tại
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Duyệt qua các thư mục từ MONTH_01 đến MONTH_12
for month in range(1, 13):
    month_folder = os.path.join(root_folder, f'MONTH_{month:02}')

    # Duyệt qua các file trong thư mục "data"
    data_folder = os.path.join(month_folder, 'data')
    if os.path.exists(data_folder):
        for file_name in os.listdir(data_folder):
            if file_name.endswith(('.shp', '.shx')):
                file_path = os.path.join(data_folder, file_name)
                shutil.move(file_path, destination_folder)

    # Duyệt qua các file .tif trong thư mục month_folder
    for file_name in os.listdir(month_folder):
        if file_name.endswith('.tif'):
            file_path = os.path.join(month_folder, file_name)
            shutil.move(file_path, destination_folder)

print("Tất cả các file đã được di chuyển thành công!")
