import geopandas as gpd

# Path to your .shp file
shapefile_path = "/Users/attaullah/Downloads/cb_2018_us_division_500k/cb_2018_us_division_500k.shp"

# Load shapefile into a GeoDataFrame
gdf = gpd.read_file(shapefile_path)

# Display the first few rows
print(gdf.head())

# Access geometries and attributes
print(gdf.geometry)
