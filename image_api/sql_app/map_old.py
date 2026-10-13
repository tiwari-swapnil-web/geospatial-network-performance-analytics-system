# uvicorn image_api.sql_app.main:app --port 8000 --reload
# uvicorn sql_app.main:app --port 8000 --reload
# uvicorn main:app --port 8000 --reload

from typing import List, Annotated

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Form
import shapely as shp
from sqlalchemy.orm import Session
from sqlalchemy import text, select, MetaData, Table
from tempfile import NamedTemporaryFile
import sqlalchemy as sqlA

from sql_app import schemas_map
from models_map import SubgridGeo
#from sql_app.crud_map import get_master_poly
from sql_app.database import SessionLocal, engine
from sql_app.functions_map import get_resource, get_elevation
import models_map

import json
import os
import pandas as pd
import geopandas as gpd
import uvicorn

"""# RETRIEVES ALL IMPORTED MODULES
import sys
from pprint import pprint
pprint(list(sys.modules.keys())) # This line prints all imported modules
"""


#############################################################################################################################

# API parameters
cpu_count = 4
API_LINK = '127.0.0.5:8000'
app = FastAPI()

models_map.Base.metadata.create_all(bind=engine)


# Other parameters (for back-end only)
str_query = """SELECT IMAGE_NAME,PT_LAT,PT_LON,BUILD_PROB,FOLIAGE_PROB,CLASS FROM predictions_geo3"""


# Establish database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#############################################################################################################################



@app.post("/map/")
def read_coords(input: Annotated[str, Form()], db: Session = Depends(get_db)):
    """
    Takes a comma-separated string as input and returns information of the region bounded by it.
    Input format: lon1,lat1,lon2,lat2,lon3,lat3,......
    """



   ################### (1) Create polygon object from input ###################
    str_list = input.split(',')

    if len(str_list) % 2 != 0 and len(str_list) < 6:
        return "WARNING: Uneven input + limited information. Keep minimum 3 coordinate pairs."
    elif len(str_list) % 2 != 0:
        return "WARNING: Uneven input. Keep PAIRS of coordinates as input."
    elif len(str_list) < 6:
        return "WARNING: A shape requires a minimum of 3 vertices. Keep minimum 3 coordinate pairs."
    else:
        coords_list = []
        i = 0
        while i <= len(str_list)-2:
            coords_list.append(shp.Point(str_list[i], str_list[i+1]))
            i+=2

    #print(coords_list)
    #print([(p.x, p.y) for p in coords_list])
    poly = shp.Polygon([(p.x, p.y) for p in coords_list])
    #print(poly)



    print("Step 1 Complete")
    ################### (2) Extract the geodata from SQL database ###################
    
    #connection = engine.connect()
    #print(connection)
    #resoverall = connection.execute(text(str_query))
    #print(resoverall)

    
    metadata = MetaData()
    table = Table(
        'predictions_geo3', 
        metadata, 
        #autoload=True, 
        autoload_with=engine
    )

    stmt = select((
        table
    ))

    conn = engine.connect()
    result = conn.execute(stmt)
    #print(list(result.keys()))
    #print(pd.DataFrame(result.fetchall(), columns=result.keys()))
    #gdf = gpd.GeoDataFrame(pd.Series(result.fetchall()), list(result.keys()))
    #print(gdf.head())
    
    gdf = pd.DataFrame(result.fetchall(), columns=result.keys())
    gdf.rename(columns={'Unnamed: 0': 'index_db'}, inplace=True)

    #print(gdf["geometry_str"].iloc[0])
    #gdf = pd.read_sql(resoverall.fetchall(), con=connection)

    '''
        gdf = pd.read_sql_query(
        sql = sqlA.select((
            SubgridGeo.id,
            SubgridGeo.image,
            SubgridGeo.pt_lat,
            SubgridGeo.pt_lon,
            SubgridGeo.build_prob,
            SubgridGeo.foliage_prob,
            SubgridGeo.class_,
            SubgridGeo.geometry_str
        )),
        con=engine
    )
    '''
    '''
    gdf = pd.read_sql_query(sql=sqlA.select(SubgridGeo), con=engine)
    '''




    print("Step 2 Complete")
    ################### (3) Filter useful info to keep using polygon of bounded region ###################
    '''Converting WKT representations to Shapely objects'''
    list_points = []
    for row in gdf.itertuples():
        #print(gdf["geometry_str"].iloc[i])
        p = shp.from_wkt(row[8])
        list_points.append(p)

    gdf["geometry"] = gpd.GeoSeries(list_points)
    



    '''Detect the bounded area'''
    gdf_inPoly = gdf[poly.contains(gdf['geometry'])==True]
    #gdf_outPoly = gdf[poly.contains(gdf['geometry'])==False]

    gdf_inPoly.drop('geometry_str', axis=1, inplace=True)
    gdf_inPoly.reset_index(drop=True, inplace=True)
    #print(gdf_inPoly)




    print("Step 3 Complete")
    ################### (4) API calls to get more detailed knowledge of bounded region ###################
    '''Elevation (AMSL)'''
    list_amsl = []
    for row in gdf_inPoly.itertuples():
        latitude = row[3]
        longitude = row[4]

        elevation = get_elevation(latitude, longitude)
        list_amsl.append(elevation)
    
    gdf_inPoly["AMSL"] = pd.Series(list_amsl).values



    #'''Information for the polygon centroid'''
    # In case of cell sector groups as input polygon, this will give the geodata for the antenna's location
    #center = shp.centroid(poly)



    '''Percentage covers of relevant classes'''
    # STATISTICS FROM GEODATA
    count_pred = gdf_inPoly['CLASS'].size
    desc_pred = gdf_inPoly['CLASS'].value_counts(normalize=True)*100

    stats = "Total number of predictions =", count_pred, desc_pred


    

    print("Step 4 Complete")
    ################### (5) Display final output to user in desired format ###################
    #print("GDF has been made")

    x = gdf_inPoly.to_json(orient="records", default_handler=str)
    x2 = json.loads(x)
    print("Step 5 Complete")
    return {"Polygon geodata":x2, "Coverage of polygon classes":stats}





#############################################################################################################################


if __name__ == '__main__': 
    host, port = API_LINK.split(':')
    uvicorn.run(
        "map:app",
        host=host,
        port=int(port),
        #factory=False,
        #reload=False,
        #loop='asyncio',
        workers=cpu_count,
    )