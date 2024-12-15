import h3
from shapely.geometry import Polygon, Point
import numpy as np
import pandas as pd
import random

def softmax(x): 
    exp_x = np.exp(x - np.max(x))  # Avoid overflow issues
    return exp_x / np.sum(exp_x)

class Heatmap:
    def __init__(self, file):
        self.heatmap_resolution = 7
        self.generate_heatmap(file)
    
    def generate_heatmap(self, file):
        # Load the CSV file and generate the heatmap
        columns = ['idx', 'label', 'location.lat', 'location.long']
        df = pd.read_csv(file, usecols=columns)
        heatmap_resolution = 6
        # Use geo_to_h3 instead of the deprecated latlng_to_cell
        df['heatmap'] = df.apply(lambda row: h3.geo_to_h3(row['location.lat'], row['location.long'], heatmap_resolution), axis=1)
        heatmap_counts = df['heatmap'].value_counts().reset_index()
        heatmap_counts.columns = ['heatmap', 'occurrences']
        self.dict = {row[0]: row[1] for row in heatmap_counts.values}

    def sample(self, h3_region_id):
        # Get child cells of the given region at the specified resolution
        cells = np.array(list(h3.h3_to_children(h3_region_id, self.heatmap_resolution))) 
        values = [self.dict.get(key, 0) for key in cells]
        selected_cell = np.random.choice(cells, p=softmax(values))      

        # Get the polygon vertices of the H3 region
        hexagon_vertices = h3.h3_to_geo_boundary(str(selected_cell), geo_json=False)
        
        # Create a Shapely Polygon from the vertices
        hexagon_polygon = Polygon([(lon, lat) for lat, lon in hexagon_vertices])
        
        # Generate a random point inside the polygon
        min_x, min_y, max_x, max_y = hexagon_polygon.bounds
        while True:
            random_point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
            if hexagon_polygon.contains(random_point):
                break
        
        return [random_point.x, random_point.y]
