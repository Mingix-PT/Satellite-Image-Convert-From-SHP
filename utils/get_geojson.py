import rasterio
from rasterio.features import shapes
import json

# Open the TIFF file
with rasterio.open('sentinel/data/anh_25km.tif') as src:
    # Read the first band
    band = src.read(1)

    # Open the output file
    output_file = 'sentinel.geojson'
    with open(output_file, 'w') as f:
        # Write the initial part of the GeoJSON
        f.write('{"type": "FeatureCollection", "features": [')

        first = True
        for i, (s, v) in enumerate(shapes(band, transform=src.transform)):
            if not first:
                f.write(',')
            else:
                first = False

            feature = {
                'type': 'Feature',
                'properties': {'raster_val': v},
                'geometry': s
            }
            f.write(json.dumps(feature))

        # Write the closing part of the GeoJSON
        f.write(']}')

print(f"GeoJSON saved to {output_file}")
