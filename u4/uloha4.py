# -*- coding: utf-8 -*-
import requests
import zipfile
import csv
import os
import geopandas as gpd

def download_file(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, "wb") as file:
            file.write(response.content)
        print("File downloaded successfully.")
    else:
        print("Failed to download the file.")

def extract_zip(zip_file, extract_path):
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    print("ZIP file extracted successfully.")

def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

# Setting dictionary path
path_in = input("Zadejte cestu pro ulozeni souboru: ")
os.chdir(path_in)

url = "https://www.cuzk.cz/CUZK/media/CiselnikyISUI/UI_OBEC/UI_OBEC.zip?ext=.zip"
zip_file_name = "RUIAN_OBCE.ZIP"  # ZIP file name
csv_file_name = "UI_OBEC.csv"  # CSV file name

# Download the ZIP file
download_file(url, zip_file_name)

# Check if the ZIP file was downloaded successfully
if not os.path.exists(zip_file_name):
    print("Failed to download the ZIP file.")
    exit()

# Extract the ZIP file
extract_zip(zip_file_name, ".")

# Check if the CSV file exists
if not os.path.exists(csv_file_name):
    print("CSV file not found.")
    exit()

obce_kody = {}  # Empty dictionary to store codes and names

# Read the CSV file and save the first and second fields to the dictionary
with open(csv_file_name, 'r', encoding='cp1250') as csv_file:
    reader = csv.reader(csv_file, delimiter=';')
    next(reader)  # Skip the header row
    for row in reader:
        obce_kody[row[1]] = row[0]

print("Data saved to the dictionary successfully.")

# Prompt the user for name of the city
while True:
    city_in = input("Zadejte nazev obce: ")
    if city_in in obce_kody:
        break
    else:
        print("Neplatny nazev obce. Zadejte znovu.")

# Retrieve the code for the entered city
code_out = obce_kody.get(city_in)

print("Kod pro obec", city_in, "je", code_out)
print("Stahuji prislusny CSV soubor")

url = "https://vdp.cuzk.cz/vymenny_format/csv/20230430_OB_{0}_ADR.csv.zip".format(code_out)
file_name = "20230430_OB_" + code_out + "_ADR.csv.ZIP" # Specify the desired file path

# Download the CSV file
download_file(url, file_name)

# Check if the CSV file was downloaded successfully
if not os.path.exists(file_name):
    print("Failed to download the file.")
    exit()

# Extract the CSV file
extract_zip(file_name, ".")

input_file = "20230430_OB_%s_ADR.csv" % code_out
error = True

ulice = set()  # Set to store unique street names

# Open the input CSV file and extract street names
with open(input_file, 'r') as input_csv:
    reader = csv.reader(input_csv, delimiter=';')
    next(reader)  # Skip the header row
    for row in reader:
        street_name = row[10].strip()
        if street_name:
            ulice.add(street_name)
        else: 
            obec = row[8].strip()
            ulice.add(obec)

# Prompt the user for the street name
while True:
    street_in = input("Zadejte nazev ulice (pokud není, zadejte nazev mestke casti): ")
    if street_in in ulice:
        break
    else:
        print("Neplatny nazev ulice. Zadejte znovu.")

# Open the input and output CSV files
output_file = "adresni_mista_%s_%s.csv" % (city_in, street_in)
with open(input_file, 'r', encoding='cp1252') as input_csv, open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
    # Create CSV reader and writer objects
    reader = csv.reader(input_csv, delimiter=';')
    next(reader)  # Skip the first line
    writer = csv.writer(output_csv, delimiter=';')
    headerline = ['Ulice', 'Typ_SO', 'Cislo_domu', 'Cislo_or', 'Naz_casti', 'PSC', 'Y', 'X']
    
    # Write the header line to the output CSV file
    writer.writerow(headerline)

    # Process each row in the input CSV file
    for row in reader:
        street_name = row[10].strip()
        so=row[11]
        cp = row[12]
        co = row[13]
        mesto = row[8]
        psc_raw = row[15].strip()
        psc = psc_raw[:3] + " " + psc_raw[3:]
        if row[16] and row[17]:  # Check if the value is not empty
            X = -float(row[16])
            Y = -float(row[17])
        else:
            X = 0.0  # Assigning 0.0 as the default value
            Y = 0.0  # Assigning 0.0 as the default value


        if street_name == "":
            street_name = mesto

        if street_name == street_in:
            writer.writerow([street_name, so, cp, co, mesto, psc, X, Y])  # Write the modified row to the output CSV file

# Remove the downloaded files
remove_file(input_file)
remove_file(zip_file_name)
remove_file(csv_file_name)
remove_file(file_name)

# Read the CSV file using pandas
dataframe = gpd.read_file(output_file, encoding='utf-8')

# Convert the DataFrame to a GeoDataFrame
geodataframe = gpd.GeoDataFrame(dataframe, geometry=gpd.points_from_xy(dataframe['Y'], dataframe['X']))

# Assign the EPSG 5514 coordinate system to the GeoDataFrame
geodataframe.crs = "EPSG:5514"

# Save the GeoDataFrame to a shapefile
output_shapefile = "adresni_mista_{}_{}.shp".format(city_in, street_in)
geodataframe.to_file(output_shapefile, driver='ESRI Shapefile')

# Read the shapefile containing roads using geopandas
roads = gpd.read_file('road.shp', encoding='cp1250')

# Select features based on an attribute value
selected_features = roads[roads['ON'] == street_in]

# Check if selected_features is empty
if not selected_features.empty:
    # Save the GeoDataFrame to a shapefile
    output_roads = "roads_{}.shp".format(street_in)
    selected_features.to_file(output_roads, driver='ESRI Shapefile')
    print("Street",street_in,"selected")
else:
    print("No features matched the attribute value ", street_in)
    exit()


# Read the point shapefile
point_shp = gpd.read_file(output_shapefile, encoding='cp1250')

# Read the line shapefile
line_shp = gpd.read_file(output_roads, encoding='cp1250')

from shapely.geometry import Point

dist = []

for point in point_shp.geometry:
    nearest_distance = min(line_shp.geometry.distance(point))
    dist.append(nearest_distance)

point_shp['dist'] = dist

point_shp.to_file("point_dist_{}.shp".format(street_in))

print("Distances generated")
