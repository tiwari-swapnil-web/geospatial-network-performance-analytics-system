# Introduction

A high-level summary that covers the following areas:

- general overview of the model training, prediction and API scripts
- modules used in the back-end
- algorithmic flow of the scripts

For internal use only. Contains sensitive information pertaining to various geographical locations. Handle the information carefully.

# Overview

The IMAGE module is designed to create a solution that enables quick, efficient analysis of geographical regions and extraction of the results.

This README briefly describes the overall flow of the IMAGE process, from initial model training to predictive analysis of a large geographical region to generate geodata, and finally to the extraction of analyzed geodata.

The figure below shows the general IMAGE high-level flow diagram:

![](images-readme/image1.png)

# Software Requirements

Before the solution is implemented, the following software prerequisites need to be satisfied:

- QGIS Desktop (>=3.22.8)
- Python installation (>=3.10.11)

Python module requirements for model training/predictions:

| **Package**   | **Version** | **CMD command**                     |
| ------------- | ----------- | ----------------------------------- |
| area          | 1.1.1       | pip install area==1.1.1             |
| gdal          | 3.4.3       | pip install gdal==3.4.3             |
| geopy         | 2.4.1       | pip install geopy==2.4.1            |
| keras         | 2.15.0      | pip install keras==2.15.0           |
| matplotlib    | 3.8.4       | pip install matplotlib==3.8.4       |
| numpy         | 1.26.4      | pip install numpy==1.26.4           |
| opencv-python | 4.8.0.76    | pip install opencv-python==4.8.0.76 |
| pandas        | 2.1.4       | pip install pandas==2.1.4           |
| pillow        | 10.3.0      | pip install pillow==10.3.0          |
| pyproj        | 3.7.0       | pip install pyproj==3.7.0           |
| scikit-image  | 0.21.0      | pip install scikit-image==0.21.0    |
| scikit-learn  | 1.4.2       | pip install scikit-learn==1.4.2     |
| seaborn       | 0.12.2      | pip install seaborn==0.12.2         |
| shapely       | 2.0.1       | pip install shapely==2.0.1          |
| tensorflow    | 2.15.0      | pip install tensorflow==2.15.0      |

Python module requirements for IMAGE API:

| **Package** | **Version** | **CMD command**                 |
| ----------- | ----------- | ------------------------------- |
| fastapi     | 0.115.5     | pip install fastapi==0.115.5    |
| geopandas   | 0.14.3      | pip install geopandas==0.14.3   |
| Levenshtein | 0.26.1      | pip install Levenshtein==0.26.1 |
| numpy       | 1.26.4      | pip install numpy==1.26.4       |
| pandas      | 2.1.4       | pip install pandas==2.1.4       |
| pyproj      | 3.7.0       | pip install pyproj==3.7.0       |
| requests    | 2.31.0      | pip install requests==2.31.0    |
| shapely     | 2.0.1       | pip install shapely==2.0.1      |
| uvicorn     | 0.25.0      | pip install uvicorn==0.25.0     |

# IMAGE Overall Operation

The following steps illustrate how to create the image which can be used for creating training dataset for the model and also during predictions/validations.

## Data Preparation

There can be two types of inputs for the solution depending upon the phase where it is used. To train the model, a certain set of inputs are required while during the prediction process.

### Setting up QGIS layers

- In QGIS Desktop, select Project🡪New to create a new project.
- Add the following layers:
  - Google Satellite; via plugin "QuickMapServices"
  - Polygon Boundary: indicates area to perform model training over
- For Polygon Boundary, select Layer🡪Toggle Editing, and then Edit🡪Add Rectangle🡪Add Rectangle from Extent. Drag the cursor to map the sides of this rectangular polygon over the desired area for analysis.

![](images-readme/image2.png)

![](images-readme/image3.png)

![](images-readme/image4.png)

![](images-readme/image5.png)

### Bounding of area via Satellite and polygon

- For Google Satellite layer, right-click and select Export🡪Save As.
- Define the options as shown in the screenshot below, then click OK to generate a .tiff file version of the bounded map region.

![](images-readme/image6.png)

- Notes:
  - Since 0.001 deg is 111m hence the conversions and calculations for Resolution and North, East, South, West we have used the same calculation by unitary method.
  - North, East, South, West extremities which came in upon selecting the Calculate from Layer are updated with a buffer of 250metres to include the boundaries better.
  - North and East have the buffer degrees added while South and West are subtracted to include the region within it

### Creation of image dataset from .TIFF file

- Select the layer generated in the previous step. Right-click and select Export🡪Save As.
- Define the operations as shown in the screenshot below, then click OK to generate multiple smaller .tif files encompassing the bigger .tiff file contents.

![「 alc 0 「 「 0 彐 1h2
L r6n10- n
Keep
the 14

- ~ 1000
  g59052g , g193
  , i n 一 P501437
  0
  — 3330337 E73
- 0 71192
  26013 51
  K22 1h2 0
  50 : 舜
- t 「 R53 EPSG 857f21h2
  0
  1223X183 一 h 523n 53 n
  10 0 new
  Pyoson 3 & u : 0 TO
  Ch k 「 「 20
  「 「 h Clickthe
  6n0 = rmge ; eofAOI
  0
  0
  0
  0 ](images-readme/image7.png)

- Notes:
  - To Browse and change the CRS, search for the "EPSG:3857" CRS and apply.

The above steps result in a folder with \[1000 pixel X 1000 pixel\] size image covering \[500m X 500m\] surface area in ".tiff" format image files, which is the desired Area of Interest for the model.

## Process Flow for Building Data Preparation

This section discusses the steps involved in training data creation and simplistic way how for data annotation. The training data that is used for model training is a combination of 50mX50m images (approx 80 % images) and 100mX100m images (approx 20 % images). To create these images from the images created earlier follow the below steps.

### Assigning variables in code "imageObjectDetection-DataCollector"

- Assign the variable of "chunksize" . This variable determines the output shape of the image, i.e., 50m X 50m for chunksize 50 or 100m X 100m for chunksize of 100.
- Configure the paths to the output tiffs of size 500m X 500m tiffs.
- image_path - Update the path to the input tiff fil that will be used to create training data and for annotation. \[ Needs update for every image file during the labelling process\]
- outpath - Enter the path where the labelled training data in different folders will be stored. \[This needs to be updated only once\]

### Execution of the code "imageObjectDetection-DataCollector" - Training data creation for Buildings

- The Jupyter notebook has multiple cells, while two cells for data creation and annotation is marked with "Building" and another as "Other".
- Users need to run all the common cells in the beginning one by one followed by the cell which is marked with Building every time.
- This process ensures we create the building data first and then check for something different. This has been found to be easy and faster during the different iterations developers has performed with the solution.

### Data annotation and training data creation – Building

Execute the cell as highlighted above to find a new window open up based on the picture chosen.

Note: User must only click on the grids after careful consideration on what is the category of the building as it cannot be undone. Also, the user should click on the grids where they see the class covering most portions of it (which turns red upon clicking it) and not the opposite grids.

### Run several iterations of the above steps for creating the complete data set for Building

Repeat the steps mentioned before this for each viable .tiff file to obtain robust training datasets for Building class.

### Execution of the code "imageObjectDetection-DataCollector" - Training data creation for Other

To run the data creation and labeling for the other class follow the same process as above now using the Notebook Cell marked with "Other" and skip the one marked with "Building"

## Process Flow for Foliage Data Preparation

To run the steps for vegetation run the notebook named "imageObjectDetection-DataCollector_foliage"

To run the process for Vegetation, steps remain same where building is replaced with trees.

The other class of Vegetation/Foliage training includes anything which doesn't have big trees, i.e., Grasslands, Farmlands, Lake, Building, roads etc.

## Important Notes for Data Preparation

If the building section is ran, then users need to click on those cells where they see mostly buildings and close the window to save all those grid images under corresponding folder labelled.

Once a grid is selected it cannot be undone hence careful consideration must be made before clicking.

Selection of the grids are recommended to be done when a grid is covered mostly by the item of concern or has some unique features.

Repeat the steps to create good number of labelled training data.

## Directory Structure

Upon completion of the training data preparation steps above, following folders with labelled folder name will be created in the output folder which can be used in the model training phase.

**Vegetation/ Foliage output folder**

![This PC New Volume
Name
a Other
a
vegetation
IMAGEPRO
modeldata_foliage
Date modified
16-06-2023 DO: 16
16-06-2023 DO: 18
Type
File folder
File folder
Size ](images-readme/image8.png)

&nbsp;

**Building output folder**

![This PC New Volume
Name
building
n Other
IMAGEPRO
mode Idata
Date modified
14-06-2023 01:09
14-06-2023 01: 10 ](images-readme/image9.png)

## Algorithmic Flow for IMAGE model training + model predictions

### Dataset Creation

![](images-readme/image10.png)

### Model Training

![](images-readme/image11.png)![](images-readme/image12.png)

### Model Predictions

![](images-readme/image13.png)

![](images-readme/image14.png)

## API Structure

![](images-readme/image15.png)
