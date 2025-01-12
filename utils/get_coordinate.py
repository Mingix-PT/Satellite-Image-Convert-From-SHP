import rasterio
from shapely.geometry import mapping, Polygon
import json

# Open the TIFF file
with rasterio.open('sentinel/data/anh_25km.tif') as src:
    # Get the coordinates of the image's boundary
    bounds = src.bounds
    corners = [
        (bounds.left, bounds.top),
        (bounds.right, bounds.top),
        (bounds.right, bounds.bottom),
        (bounds.left, bounds.bottom)
    ]
    polygon = Polygon(corners)

# Convert the polygon to GeoJSON format
geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": mapping(polygon)
        }
    ]
}

# Save GeoJSON to a file
output_file = 'sentinel_bounds.geojson'
with open(output_file, 'w') as f:
    json.dump(geojson, f)

print(f"GeoJSON saved to {output_file}")
