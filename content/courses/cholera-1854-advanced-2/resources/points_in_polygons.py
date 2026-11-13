import geopandas as gpd
import pandas as pd

def points_in_polygons(points_gdf, polygons_gdf):
    
    polygons = polygons_gdf
    points = points_gdf
    
    # Make a copy because I'm going to drop points as I
    # assign them to polys, to speed up subsequent search.
    pts = points.copy() 

    # We're going to keep a list of how many points we find.
    pts_in_polys = []

    # Loop over polygons with index i.
    for i, poly in polygons.iterrows():

        # Keep a list of points in this poly
        pts_in_this_poly = []

        # Now loop over all points with index j.
        for j, pt in pts.iterrows():
            if poly.geometry.contains(pt.geometry):
                # Then it's a hit! Add it to the list,
                # and drop it so we have less hunting.
                pts_in_this_poly.append(pt.geometry)
                pts = pts.drop([j])

        # We could do all sorts, like grab a property of the
        # points, but let's just append the number of them.
        pts_in_polys.append(len(pts_in_this_poly))

    # Add the number of points for each poly to the dataframe.
    polygons['points_in_polygon'] = pd.Series(pts_in_polys)
    
    return polygons
