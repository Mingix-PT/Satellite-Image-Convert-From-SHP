import os
import geopandas as gpd
import rasterio
from PIL import Image, ImageDraw

# List of shapefiles and their corresponding colors
shapefiles = [
    ('final_sample/HoangHoa_MONTH_01_0_0_0_residential.shp', 'yellow'),
    ('final_sample/HoangHoa_MONTH_01_0_0_0_rice_field.shp', 'red'),
    ('final_sample/HoangHoa_MONTH_01_0_0_0_forest.shp', 'green'),
    ('final_sample/HoangHoa_MONTH_01_0_0_0_water.shp', 'blue'),
    ('final_sample/HoangHoa_MONTH_01_0_0_0_unidentifiable.shp', 'white'),
]

# Open the TIF image to get its dimensions
tif_image_path = 'final_sample/HoangHoa_MONTH_01_0_0_0.tif'
with rasterio.open(tif_image_path) as src:
    width = src.width
    height = src.height
    transform = src.transform

# Create a blank image with the same dimensions as the TIF image
image = Image.new('RGB', (width, height), (0, 0, 0))
draw = ImageDraw.Draw(image)

# Function to convert geographic coordinates to pixel coordinates
def geo_to_pixel(x, y, transform):
    col = int((x - transform.c) / transform.a)
    row = int((y - transform.f) / transform.e)
    return col, row

# Iterate over the list of shapefiles and draw their polygons onto the image
for shapefile_path, color in shapefiles:
    gdf = gpd.read_file(shapefile_path)
    for geom in gdf.geometry:
        if geom.geom_type == 'Polygon':
            exterior_coords = [geo_to_pixel(x, y, transform) for x, y in geom.exterior.coords]
            draw.polygon(exterior_coords, fill=color)
        elif geom.geom_type == 'MultiPolygon':
            for polygon in geom:
                exterior_coords = [geo_to_pixel(x, y, transform) for x, y in polygon.exterior.coords]
                draw.polygon(exterior_coords, fill=color)

# Save the image as a PNG file
output_folder = 'output_images'
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, 'HoangHoa_MONTH_01_0_0_0_combined.png')
image.save(output_path)

print(f"Image saved to {output_path}")
