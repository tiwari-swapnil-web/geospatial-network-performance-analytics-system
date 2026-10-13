import json
import shapely as shp
from shapely.geometry import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.ops import unary_union, transform
from functools import partial
import pyproj
import re
import requests
import sqlite3
import pandas as pd
import geopandas as gpd
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
import Levenshtein



# Supporting functions
def get_area(polygon: Polygon):
    """Returns the total area for a given polygon input.

    Args:
        polygon (Polygon): Polygon obtained from initial API input.

    Returns:
        float: Total area of the polygon input.
    """
    poly_area = transform(
    partial(
        pyproj.transform,
        pyproj.Proj(init='EPSG:4326'),
        pyproj.Proj(
            proj='aea',
            lat_1=polygon.bounds[1],
            lat_2=polygon.bounds[3]
        )
    ),
    polygon)

    return poly_area.area



def calculate_distance(lon1: float, lat1: float, lon2: float, lat2: float):
    """Returns the geographical distance between two points on a map.

    Args:
        lon1 (float): Longitude value at point 1.
        lat1 (float): Latitude value at point 1.
        lon2 (float): Longitude value at point 2.
        lat2 (float): Latitude value at point 1.

    Returns:
        float: Distance between two points.
    """    
    # Convert latitude and longitude from degrees to radians
    lon1 = radians(lon1)
    lat1 = radians(lat1)
    lon2 = radians(lon2)
    lat2 = radians(lat2)

    # Haversine formula to calculate the distance
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Radius of Earth in kilometers. Use 3956 for miles. Determines return value units.
    r = 6371.0
    distance = r * c

    return distance



def runSQL_cluster(url_db: str):
    """Runs an SQL query and returns its output

    Args:
        url_db (str): SQL query to run.

    Returns:
        DataFrame: Pandas dataframe containing query results.
    """    
    conn = sqlite3.connect(url_db)
    query = "select * from " + "cluster_centres" + " order by area" + ";"
    res = pd.read_sql_query(query, conn)

    return res



def get_resource(r):
    resourceSets = json.loads(r.text)
    try:
        for resource in resourceSets['resourceSets']:
            return [rsc for rsc in resource['resources']]
    except KeyError:
        try:
            resourcesSets = resourceSets['Response']['ResourceSets']
            resourceSet = resourcesSets['ResourceSet']
            if isinstance(resourceSet, dict):
                return resourceSet['Resources']
            elif isinstance(resourceSet, list):
                return [rsc for rsc in resourceSet['Resources']]
        except KeyError:
            print(KeyError)



def get_elevation(lat, lon):
    key = 'Ap2jFsGK3XZxoJYoaoE8pMLEk2B4x8OqgkolcqfDPwN-24_V9Vd__m5YOCyXPXch'
    point_query = f"{lat},{lon}"
    api_query = f'http://dev.virtualearth.net/REST/v1/Elevation/List?points={point_query}&heights=sealevel&key={key}'
    
    r = requests.get(api_query)
    if r.status_code != 200:
        raise r.raise_for_status()

    resource = get_resource(r)
    elevation = resource[0]['elevations'][0]

    return elevation



# MAIN FUNCTIONS
def format_input(input: str):
    """Takes a comma-separated string as input and returns a nested list of coordinates.

    Args:
        input (str): List of coordinates for a polygon; 
                    Each coordinate value separated by comma (',')
                    Format: lon1,lat1,lon2,lat2,lon3,lat3,......

    Returns:
        list: List of coordinates
    """
    translation_table = str.maketrans('', '', ' ')
    str_wo_space = input.translate(translation_table)
    pattern = re.compile('[^0-9.,]')
    print(input)

    if re.search(pattern, str_wo_space):
        return "WARNING: Invalid characters detected. Should only have numbers 0-9, full-stops and commas."

    str_list = str_wo_space.split(',')

    # Checks to ensure valid user input is given
    if str_list == ['']:
        return "WARNING: No coordinate input given."
    elif len(str_list) % 2 != 0 and len(str_list) < 6:
        return "WARNING: Uneven input + limited information. Keep minimum 3 coordinate pairs."
    elif len(str_list) % 2 != 0:
        return "WARNING: Uneven input. Keep PAIRS of coordinates as input."
    elif len(str_list) < 6:
        return "WARNING: A shape requires a minimum of 3 vertices. Keep minimum 3 coordinate pairs."
    else:
        return str_list



def read_coordinates(str_list: str):
    """Takes a list of coordinates as input and returns a polygon object of the region bounded by it.

    Args:
        str_list (str): List of coordinates for a polygon.
                        Format: [lon1,lat1,lon2,lat2,lon3,lat3,......]

    Returns:
        shapely.geometry.Polygon: Shapely polygon bounded by the coordinate input.
    """    

    coords_list = []
    i = 0
    #print(str_list)
    while i <= len(str_list)-2:
        coords_list.append(shp.Point(str_list[i], str_list[i+1]))
        i+=2

    polygon = shp.Polygon([(p.x, p.y) for p in coords_list])

    return polygon



def find_nearest_cluster(polygon: Polygon, df: pd.DataFrame):
    """Returns the name of the cluster closest to a given polygon.

    Args:
        polygon (Polygon): Polygon obtained from initial API input.
        df (DataFrame): Dataframe containing information on the location names and coordinates of their centroids.

    Returns:
        str: Name of the cluster taken directly from the dataframe.
    """    
    closest_area = ""
    closest_dist = 10**10

    poly_centroid = list(polygon.centroid.coords)
    poly_centroid = poly_centroid[0]


    for idx in df.index:
        temp_dist = (df["centre_lon"][idx],df["centre_lat"][idx])
        closest_dist_1 = calculate_distance(float(poly_centroid[0]),
                                               float(poly_centroid[1]),
                                               float(temp_dist[0]),
                                               float(temp_dist[1])
                                               )
        if closest_dist_1 < closest_dist:
            closest_dist = closest_dist_1
            closest_area = df["area"][idx]

    return closest_area



def get_cluster_name(location: str, url_db: str, polygon: Polygon):
    """Takes the name of a location and returns a match from the SQL database.

    Args:
        location (str): Name of desired geographic location (city) provided as part of the initial API call. 
                        If no location given (==None), function automatically determines the most appropriate cluster.
        url_db (str): File address of the SQL database housing information on all locations with associated geodata.
                        Predefined in the API script; change in case of files being moved.
        polygon (Polygon): Polygon obtained from initial API input.

    Returns:
        str: Name of the location as given in the SQL database, if present.
    """
    df = runSQL_cluster(url_db)

    if location == "":
        cluster_name = find_nearest_cluster(polygon, df)
        return cluster_name

    word = location.lower()

    idx_lev_most = 0
    most_similar = df["area"][idx_lev_most]
    lev_most = float(Levenshtein.ratio(word, most_similar))

    
    for idx in df.index:
        lev = float(Levenshtein.ratio(word, df["area"][idx]))
        if lev > lev_most:
            lev_most = lev
            idx_lev_most = idx

    cluster_name = df["area"][idx_lev_most]

    if lev_most >=0.8:
        return cluster_name
    else:
        return None
    


def get_df_from_sql(url_db: str, table_name: str):
    """Returns the dataset of the dessired geographical region.

    Args:
        url_db (str): File address of the SQL database housing information on all locations with associated geodata.
                        Predefined in the API script; change in case of files being moved.
        table_name (str): Name of the dataset for a given region.

    Returns:
        DataFrame: Dataframe corresponding to the desired dataset.
    """    
    conn = sqlite3.connect(url_db)
    #cur = conn.cursor()

    query = "select * from " + table_name + ";"
    #cur.execute(query)

    #df = pd.DataFrame(cur.fetchall(), columns=cur)
    df = pd.read_sql_query(query, conn)
    df.rename(columns={'Unnamed: 0': 'index_db'}, inplace=True)

    return df



def filter_geodata(polygon: Polygon, df: pd.DataFrame):
    """Takes a dataframe and a polygon, and returns a filtered dataset corresponding to that sequence.

    Args:
        polygon (Polygon): Polygon obtained from initial API input.
        df (DataFrame): Dataframe containing geodata for a specific location.

    Returns:
        GeoDataFrame: Geopandas dataframe containing geodata exclusively for the given polygon input.
    """    
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.PT_LON, df.PT_LAT), crs="EPSG:4326")
    
    gdf["overlap"] = gdf.intersects(polygon)
    gdf_inPoly = gdf[gdf["overlap"]==True]

    return gdf_inPoly



def append_elevationData(gdf_inPoly: gpd.GeoDataFrame):
    """Returns the geodata with elevation information.

    Args:
        gdf_inPoly (GeoDataFrame): Geopandas dataframe containing geodata exclusively for the given polygon input.

    Returns:
        GeoDataFrame: Geopandas dataframe containing input geodata with elevation data.
    """    
    list_amsl = []
    for row in gdf_inPoly.itertuples():
        latitude = row[2]
        longitude = row[3]

        elevation = get_elevation(latitude, longitude)
        #print(latitude, longitude)
        list_amsl.append(elevation)
    
    gdf_inPoly["Elevation (m)"] = pd.Series(list_amsl).values

    return gdf_inPoly



def get_stats(gdf_inPoly: gpd.GeoDataFrame, polygon: Polygon):
    """Returns statistical information for the filtered geodata (total predictions, total area, distribution of map elements).

    Args:
        gdf_inPoly (GeoDataFrame): Geopandas dataframe containing geodata exclusively for the given polygon input.
        polygon (Polygon): Polygon obtained from initial API input.

    Returns:
        list: A list of dictionaries containing the statistics as key-value pairs.
    """    
    count_pred = gdf_inPoly['CLASS'].size
    desc_pred = gdf_inPoly['CLASS'].value_counts(normalize=True)*100
    area = get_area(polygon)

    stats = [
            {"Total number of predictions": count_pred}, 
            {"Surface area of region (m^2)": area},
            {"Percentage distribution of classes": desc_pred.to_dict()}
            ]

    return stats



def output_as_dict(gdf_inPoly: gpd.GeoDataFrame, polygon: Polygon, option_getStats=True):
    """Returns the filtered geodata in the form of a JSONable disctionary.

    Args:
        gdf_inPoly (GeoDataFrame): Geopandas dataframe containing geodata exclusively for the given polygon input.
        polygon (Polygon): Polygon obtained from initial API input.
        option_getStats (bool, optional): Provides option to include statistics from the function "get_stats". Defaults to True.

    Returns:
        dict: Dictionary containing the geodata.
    """    
    x1 = gdf_inPoly.to_json()
    x2 = json.loads(x1)
    x3 = [f["properties"] for f in x2["features"]]

    out = {
           "Polygon geodata": x3
          }
    
    if option_getStats==True:
        stats = get_stats(gdf_inPoly, polygon)
        out["Coverage of polygon classes"] = stats

    return out



def display_output(output):
    return output



def save_output_as_json(output, region):
    contents = json.dumps(output, indent=4)

    now = datetime.now()
    dt_string = now.strftime("%Y%m%d_%H%M%S")
    filename_json = region+"_"+dt_string+".json"

    # Writing output to new JSON file
    with open(filename_json, "w") as outfile:
        outfile.write(contents)

    return "The geodata has been saved"



def save_output_as_csv(output, region, option_getStats=True):
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d_%H%M%S")

    geodata = output["Polygon geodata"]
    filename_geo_csv = dt_string+"_"+"geo"+"_"+region+".csv"
    df_geo = pd.DataFrame.from_dict(geodata)
    df_geo.to_csv(filename_geo_csv, index=False)

    if option_getStats==True:
        statistics = output["Coverage of polygon classes"][1]["Percentage distribution of classes"]
        stats_pred_count = output["Coverage of polygon classes"][0]["Total number of predictions"]
        filename_stats_csv = dt_string+"_"+"stats"+"_"+region+".csv"
        df_stats = pd.DataFrame.from_dict(statistics, orient='index', columns=['Cover (%)'])
        df_stats.to_csv(filename_stats_csv)
    
    #print(statistics)
    #print(df_geo.head())
    #print(df_stats)

    return "Data saved in CSV format."




# SQL FUNCTION FOR TESTING PURPOSES
'''
def runSQL_subgrid(url_db: str, table_name: str):
    conn = sqlite3.connect(url_db)
    #cur = conn.cursor()

    query = "select * from " + table_name + ";"
    #cur.execute(query)

    #df = pd.DataFrame(cur.fetchall(), columns=cur)
    res = pd.read_sql_query(query, conn)

    return res
'''


# Old Version of existing functions
'''
def remove_substrings_from_end(string, substring_list):
    for substring in substring_list:
        if string.endswith(substring):
            return string[:-len(substring)]
        return string



def find_nearest_cluster_old(polygon: Polygon, json_centroids: dict):
    dict_dist = {}
    poly_centroid = list(polygon.centroid.coords)
    poly_centroid = poly_centroid[0]

    f = open(json_centroids)
    data = json.load(f)
    #print(data)

    for region, coords in data.items():
        dict_dist[region] = calculate_distance(float(poly_centroid[0]),
                                               float(poly_centroid[1]),
                                               float(coords[0]),
                                               float(coords[1])
                                               )

    min_dist = min(dict_dist.values())
    min_dist_region = list(dict_dist.keys())[list(dict_dist.values()).index(min_dist)]
    #print(min_dist_region)

    return [min_dist, min_dist_region]



def filter_geodata_old(poly: Polygon, df: pd.DataFrame):
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.PT_LON, df.PT_LAT), crs="EPSG:4326")
    #print(gdf.head(1))
    # Obtain data for overlapping region
    gdf_inPoly = gdf[poly.contains(gdf['geometry'])==True]

    return gdf_inPoly



'''
# Multi-Polygon Function Equivalents
'''
def wkt_to_boundary(poly_wkt: list):
    #list_polygons =  [shp.wkt.loads(poly) for poly in poly_wkt]
    list_polygons = [shp.wkt.loads(poly_wkt)]
    poly_multi = shp.geometry.MultiPolygon(list_polygons)
    boundary = unary_union(poly_multi)

    return boundary



def format_input_multi(input: str):
    """Takes a comma-separated, semicolon-separated string as input and returns a nested list of coordinates.

    Args:
        input (str): List of coordinates for multiple polygons; 
                    Coordinates for each polygon separated by semi-colon (';')
                    Each coordinate value separated by comma (',')
                    Format: lon1,lat1,lon2,lat2,lon3,lat3,......;lon1a,lat1a,lon2a,lat2a,lon3a,lat3a,......;......

    Returns:
        list: List of lists of coordinates; each nested list corresponds to a single polygon.
    """

    translation_table = str.maketrans('', '', ' ')
    str_wo_space = input.translate(translation_table)
    pattern = re.compile('[^0-9.,;]')

    if re.search(pattern, str_wo_space):
        return "WARNING: Invalid characters detected. Should only have numbers 0-9, full-stops, commas and/or semicolons."

    str_multiPoly = str_wo_space.split(';')
    str_list = []
    for item in str_multiPoly:
        str_list.append(item.split(','))

    # Checks to ensure valid user input is given
    for idx, item in enumerate(str_list):
        if item == ['']:
            return "WARNING: No coordinate input given."
        elif len(item) % 2 != 0 and len(item) < 6:
            return f"WARNING: Uneven input + limited information for polygon {idx+1}. Keep minimum 3 coordinate pairs."
        elif len(item) % 2 != 0:
            return f"WARNING: Uneven input for polygon {idx+1}. Keep PAIRS of coordinates as input."
        elif len(item) < 6:
            return f"WARNING: Not enough vertices for polygon {idx+1}. Keep minimum 3 coordinate pairs."
        else:
            continue

    return str_list



def read_coordinates_multi(str_list: str):
    """Takes a nested list coordinates as input and returns a list of polygon objects of the regions bounded by it.

    Args:
        str_list (str): List of listed coordinates; each nested list corresponds to coordinates of a single polygon.
                        Format: [[lon1,lat1,lon2,lat2,lon3,lat3,......],[lon1a,lat1a,lon2a,lat2a,lon3a,lat3a,......],......,[......]]

    Returns:
        list: List of Shapely polygon objects.
    """

    polygon_multi = []
    for item in str_list:
        #print(item)
        pol = read_coordinates(item)
        polygon_multi.append(str(pol))

    return polygon_multi



def get_cluster_name_multi(location: str, url_db: str, poly_wkt: list):
    """Takes the name of a location and returns a match from the SQL database.

    Args:
        location (str): Name of desired geographic location (city) provided as part of the initial API call. 
                        If no location given (==None), function automatically determines the most appropriate cluster.
        url_db (str): File address of the SQL database housing information on all locations with associated geodata.
                        Predefined in the API script; change in case of files being moved.
        poly_wkt (list): List of polygons obtained from initial API input.

    Returns:
        str: Name of the location as given in the SQL database, if present
    """
    print(poly_wkt)
    df = runSQL_cluster(url_db)

    if location == "":
        boundary = wkt_to_boundary(poly_wkt)
        cluster_name = find_nearest_cluster_old(boundary, df)
        return cluster_name

    word = location.lower()

    idx_lev_most = 0
    most_similar = df["area"][idx_lev_most]
    lev_most = float(Levenshtein.ratio(word, most_similar))

    
    for idx in df.index:
        lev = float(Levenshtein.ratio(word, df["area"][idx]))
        if lev > lev_most:
            lev_most = lev
            idx_lev_most = idx

    cluster_name = df["area"][idx_lev_most]

    if lev_most >=0.8:
        return cluster_name
    else:
        return None



def filter_geodata_multi(poly_wkt: list, df_cluster: pd.DataFrame):
    """Takes a dataframe and sequence of polygons, and returns a filtered dataset corresponding to that sequence.

    Args:
        poly_wkt (list): List of polygons obtained from initial API input.
        df_cluster (DataFrame): Dataframe containing geodata for a specific location.

    Returns:
        GeoDataFrame: Geopandas dataframe containing geodata exclusively for the given polygon input.
    """    
    gdf = gpd.GeoDataFrame(df_cluster, geometry=gpd.points_from_xy(df_cluster.PT_LON, df_cluster.PT_LAT), crs="EPSG:4326")

    boundary = wkt_to_boundary(poly_wkt)

    #gdf_inPoly = gdf[poly_multi.contains(gdf['geometry'])==True]
    #print(gdf["geometry"].intersects(poly_multi))

    gdf["overlap"] = gdf.intersects(boundary)
    gdf_inPoly = gdf[gdf["overlap"]==True]

    #print(gdf_inPoly)

    return gdf_inPoly



def get_stats_multi(gdf_inPoly: gpd.GeoDataFrame, poly_wkt: list):
    """Returns statistical information for the filtered geodata (total predictions, total area, distribution of map elements)

    Args:
        gdf_inPoly (GeoDataFrame): Geopandas dataframe containing geodata exclusively for the given polygon input.
        poly_wkt (list): List of polygons obtained from initial API input.

    Returns:
        list: A list of dictionaries containing the statistics as key-value pairs.
    """    
    count_pred = gdf_inPoly['CLASS'].size
    desc_pred = gdf_inPoly['CLASS'].value_counts(normalize=True)*100
    boundary = wkt_to_boundary(poly_wkt)
    area = get_area(boundary)
    #print(type(boundary))

    stats = [
            {"Total number of predictions": count_pred}, 
            {"Surface area of region (m^2)": area},
            {"Percentage distribution of classes": desc_pred.to_dict()}
            ]

    return stats



def output_as_dict_multi(gdf_inPoly: gpd.GeoDataFrame, poly_wkt: list, option_getStats=True):
    """Returns the filtered geodata in the form of a JSONable disctionary.

    Args:
        gdf_inPoly (GeoDataFrame): Geopandas dataframe containing geodata exclusively for the given polygon input.
        poly_wkt (list): List of polygons obtained from initial API input.
        option_getStats (bool, optional): Provides option to include statistics from the function "get_stats". Defaults to True.

    Returns:
        dict: Dictionary containing the geodata.
    """    
    x1 = gdf_inPoly.to_json()
    x2 = json.loads(x1)
    x3 = [f["properties"] for f in x2["features"]]

    out = {
           "Polygon geodata": x3
          }
    
    if option_getStats==True:
        stats = get_stats(gdf_inPoly, poly_wkt)
        out["Coverage of polygon classes"] = stats

    return out



'''