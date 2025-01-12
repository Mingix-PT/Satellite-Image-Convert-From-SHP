import rasterio

def get_number_of_channels(tif_file):
    with rasterio.open(tif_file) as src:
        num_channels = src.count
        print(f'The number of channels in the file is: {num_channels}')

# Example usage
tif_file_path = 'gg_earth_resized_dataset/test/anh_25km_gge_0_15_sat.tif'
get_number_of_channels(tif_file_path)
