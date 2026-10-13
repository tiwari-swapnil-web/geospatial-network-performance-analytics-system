import numpy as np
import pandas as pd

'''
file1 = "SUBGRID_DATA_IMAGEBASED.txt"
file2 = "SUBGRID_DATA_IMAGEBASED_NEW.txt"

df1 = pd.read_csv("SUBGRID_DATA_IMAGEBASED.txt", sep="\t")
#df2 = pd.read_csv(file2, sep="\t")

df1.head()
'''

file = "SUBGRID_DATA_IMAGEBASED_FOLIAGE_DELTA_103_EXT.txt"

df = pd.read_csv(file, sep="\t")

img_list = df['IMAGE_NAME'].unique()
print(img_list.size)