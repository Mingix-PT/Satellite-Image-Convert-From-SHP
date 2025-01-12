from PIL import Image
import rasterio
from rasterio.enums import Resampling
import os

Image.MAX_IMAGE_PIXELS = None

def resize_image(input_path, output_path, reference_image_path):
    with Image.open(reference_image_path) as ref_img:
        size = ref_img.size

    with Image.open(input_path) as img:
        img = img.resize(size, Image.LANCZOS)
        img.save(output_path)

def resize_image_to_size(input_path, output_path, size):
    if (input_path.endswith('.png')):
        with Image.open(input_path) as img:
            img = img.resize(size, Image.LANCZOS)
            img.save(output_path)

    elif (input_path.endswith('.tif')):
        with rasterio.open(input_path) as src:
            data = src.read(
                out_shape=(
                    src.count,
                    size[1],
                    size[0]
                ),
                resampling=Resampling.bilinear
            )
            transform = src.transform * src.transform.scale(
                (src.width / size[0]),
                (src.height / size[1])
            )

            profile = src.profile
            profile.update(transform=transform, width=size[0], height=size[1])

            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(data)

def resize_image_with_scale(input_path, output_path, scale):
    if (input_path.endswith('.png')):
        with Image.open(input_path) as img:
            width, height = img.size
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            img.save(output_path)

    elif (input_path.endswith('.tif')):
        with rasterio.open(input_path) as src:
            data = src.read(
                out_shape=(
                    src.count,
                    int(src.height * scale),
                    int(src.width * scale)
                ),
                resampling=Resampling.bilinear
            )
            transform = src.transform * src.transform.scale(scale, scale)

            profile = src.profile
            profile.update(transform=transform, width=int(src.width * scale), height=int(src.height * scale))

            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(data)

if __name__ == "__main__":
    # input_path = "gg_earth_25km/anh_25km_gge_mask.png"
    # output_path = "gg_earth_25km/anh_25km_gge_mask.png"
    # reference_image_path = "gg_earth_25km_png/sentinel_25km_MONTH_03_0_0_0.png"

    # resize_image(input_path, output_path, reference_image_path)
    input_folder = 'gg_earth_25km2_13band'
    # size = (12160, 8398)
    # size = (1280, 884)
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        resized_folder = input_folder + '_resized'
        output_path = os.path.join(resized_folder, filename)
        if not os.path.exists(resized_folder):
            os.makedirs(resized_folder)
        # resize_image_to_size(input_path, output_path, size)
        resize_image_with_scale(input_path, output_path, 10)
