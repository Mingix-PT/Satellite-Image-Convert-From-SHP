import rasterio
def print_image_size_rasterio(file_path):
    with rasterio.open(file_path) as dataset:
        width = dataset.width
        height = dataset.height

    print(f"Width: {width}, Height: {height}")

if __name__ == "__main__":
    file_path = "gg_earth_25km2_13band_resized/anh_25km_gge_13band_sat.tif"
    print_image_size_rasterio(file_path)
