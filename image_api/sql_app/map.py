from fastapi import FastAPI
import json
import os
import pandas as pd
import geopandas as gpd
import uvicorn

from functions_map import *


"""# RETRIEVES ALL IMPORTED MODULES
import sys
from pprint import pprint
pprint(list(sys.modules.keys())) # This line prints all imported modules
"""


#############################################################################################################################

# API parameters
CPU_COUNT = 4
API_LINK = '127.0.0.5:8000'

JSON_CENTROIDS = "C:/IMAGE/Foliage/image_api/preprocess/dataset_centroids.json"
URL_DB = "C:/IMAGE/Foliage/image_api/data/subgrids.db"


#############################################################################################################################


app = FastAPI()


@app.get("/geodata/")
def give_geodata(
                input_str: str,
                location: str,
                option_getStats: bool
                ):
    """Takes a comma-separated string as input and returns information of the region bounded by it.

    Args:
        input_str (str): Comma-separated list of coordinates for a polygon; 
                                    Each coordinate value separated by comma (',')
                                    Format: lon1,lat1,lon2,lat2,lon3,lat3,......,lonN-1,latN-1,lonN,latN
        location (str): Name of desired geographic location (city) provided as part of the initial API call. 
                        If no location given (==""), API automatically determines the most appropriate cluster.
        option_getStats (bool): Provides option to include statistics like area, % cover.

    Returns:
        dict: Dictionary containing the geodata.
    """


    ################### (1) Create polygon object from input ###################
    clean_input = format_input(input_str)
    #clean_input = format_input_multi(input_str)


    if "WARNING" in clean_input:
        return clean_input
    

    polygon = read_coordinates(clean_input)
    #polygon_wkt = read_coordinates_multi(clean_input)


    cluster_name = get_cluster_name(location, URL_DB, polygon)
    #cluster_name = get_cluster_name_multi(location, URL_DB, polygon_wkt)


    print("Step 1/4 Complete")


    ################### (2) Extract the geodata from SQL database ###################
    # Establish parameters for connection to the SQL database with all geodata


    if cluster_name is None:
        return "WARNING: Location name not recognized. Check for typos, or if location present in database table."
    

    df = get_df_from_sql(URL_DB, cluster_name)


    print("Step 2/4 Complete")


    ################### (3) Filter useful info to keep using polygon of bounded region ###################
    # Obtain data for overlapping region


    gdf_inPoly = filter_geodata(polygon, df)
    #gdf_inPoly = filter_geodata_2_multi(polygon_wkt, df)

    
    if gdf_inPoly.empty:
        #return "WARNING: No data for given polygon. Perhaps the given location name does not align with the given coordinates?"
        return "WARNING: No data for given polygon. Ensure that it's of a location with geodata present in the database."
    
    
    # If elevation data needed, uncomment below line
    #gdf_inPoly = append_elevationData(gdf_inPoly)

    print("Step 3/4 Complete")


    ################### (4) API calls to get more detailed knowledge of bounded region ###################
    

    output = output_as_dict(gdf_inPoly, polygon, option_getStats)
    #output = output_as_dict_multi(gdf_inPoly, polygon_wkt, option_getStats)


    print("Step 4/4 Complete")


    ################### (5) Obtain the final output in desired format ###################
    # Convert the dataframe to JSON representation and either 1) DISPLAY or 2) SAVE AS JSON
    

    return display_output(output)


#############################################################################################################################


if __name__ == '__main__': 
    HOST, PORT = API_LINK.split(':')
    uvicorn.run(
        "map:app",
        host=HOST,
        port=int(PORT),
        #factory=False,
        #reload=False,
        #loop='asyncio',
        workers=CPU_COUNT,
    )
