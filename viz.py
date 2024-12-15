import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import LineString

# Load data (thay bằng đường dẫn đúng)
data = np.load('.\\wild_experiments_log\\WILDGRAPH\\WILDGRAPH_EPOCHS=90_0_k0_geese.npy')

# Prepare GeoDataFrame for trajectories
lines = []
for trajectory in data:
    coords = list(zip(trajectory[:, 1], trajectory[:, 0]))  # (longitude, latitude)
    line = LineString(coords)
    lines.append(line)

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(geometry=lines, crs="EPSG:4326")  # WGS84 projection

# Plot
fig, ax = plt.subplots(figsize=(12, 12))
gdf.plot(ax=ax, color='blue', linewidth=0.5, alpha=0.7)  # Plot trajectories

# Add basemap (OpenStreetMap)
ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Adjust limits for better visualization
x_min, y_min, x_max, y_max = gdf.total_bounds
ax.set_xlim(x_min - 1, x_max + 1)
ax.set_ylim(y_min - 1, y_max + 1)

# Add labels and title
ax.set_title("WildGraph Trajectories", fontsize=16)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

plt.show()
