import os
import sqlite3
import pandas as pd
import geopandas as gpd


'''# DEFINE THE FILEPATHS TO BE USED IN THE SCRIPT'''
conndir = 'C:/IMAGE/Foliage/image_api/data/cps.db'
targetdir = "C:/IMAGE/Foliage/image_api/subgrids/"


conn = sqlite3.connect(conndir)

#wb = pd.read_excel('CPS\CPS.xlsx',sheet_name = None)

#list the files
filelist = os.listdir(targetdir)
#print("Files involved: ", filelist)

#read them into pandas
df_list = [pd.read_table(targetdir+file) for file in filelist]





'''
#concatenate them together
big_df = pd.concat(df_list)

#print(big_df.columns.to_list())
# make sure a column of Point objects is present
if "geometry" not in big_df.columns.to_list():
    big_gdf = gpd.GeoDataFrame(
    big_df, geometry=gpd.points_from_xy(
        big_df.PT_LON, 
        big_df.PT_LAT), 
        crs="EPSG:4326"
    )
    big_gdf['geometry_str'] = big_gdf.geometry.to_wkt()
    big_gdf.drop(['geometry'], axis=1, inplace=True)
    #print(big_gdf.columns.to_list())
    try:
        big_gdf.to_sql(name='predictions_geo3',con=conn,index=False)
        conn.commit()
        conn.close()
        print("GDF")
    except sqlite3.OperationalError as e:
        print("Error connecting to database:", e)

else:
    try:
        big_df.to_sql(name='predictions_geo3',con=conn,index=False)
        conn.commit()
        conn.close()
        print("DF")
    except sqlite3.OperationalError as e:
        print("Error connecting to database:", e)
'''