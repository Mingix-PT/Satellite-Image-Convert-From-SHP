import os
import geopandas as gpd

data_dir = 'final'
files = os.listdir(data_dir)
files = [f for f in files if f.endswith('.shp')]
classes = [f.split('.')[0] for f in files]
classes = [c.split('_')[-1] for c in classes]
classes = [c.split('(')[0] for c in classes]

# Unique classes
classes = list(set(classes))
classes.sort()
print(classes)

class_count = {class_name: 0 for class_name in classes}

for shapefile in files:
    shapefile_path = os.path.join(data_dir, shapefile)
    gdf = gpd.read_file(shapefile_path)
    if (len(gdf.geometry) > 0) and (geometry.is_valid for geometry in gdf.geometry):
        class_name = shapefile.split('.')[0]
        class_name = class_name.split('_')[-1]
        class_name = class_name.split('(')[0]
        class_count[class_name] += len(gdf.geometry)

print(class_count)
