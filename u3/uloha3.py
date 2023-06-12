import requests
import zipfile
import csv
import os

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
path_in = input("Zadejte cestu pro uložení souborů: ")
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
    city_in = input("Zadejte název obce: ")
    if city_in in obce_kody:
        break
    else:
        print("Neplatný název obce. Zadejte znovu.")

# Retrieve the code for the entered city
code_out = obce_kody.get(city_in)

print("Kód pro obec", city_in, "je", code_out)
print("Stahuji příslušný CSV soubor")

url = f"https://vdp.cuzk.cz/vymenny_format/csv/20230430_OB_{code_out}_ADR.csv.zip"
file_name = f"20230430_OB_{code_out}_ADR.csv.ZIP"  # Specify the desired file path

# Download the CSV file
download_file(url, file_name)

# Check if the CSV file was downloaded successfully
if not os.path.exists(file_name):
    print("Failed to download the file.")
    exit()

# Extract the CSV file
extract_zip(file_name, ".")

input_file = f"20230430_OB_{code_out}_ADR.csv"
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
    street_in = input("Zadejte název ulice (pokud není, zadejte název městké části): ")
    if street_in in ulice:
        break
    else:
        print("Neplatný název ulice. Zadejte znovu.")

# Open the input and output CSV files
output_file = f"adresni_mista_{city_in}_{street_in}.csv"
with open(input_file, 'r', encoding='cp1250') as input_csv, open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
    # Create CSV reader and writer objects
    reader = csv.reader(input_csv, delimiter=';')
    writer = csv.writer(output_csv, delimiter=';')

    # Process each row in the input CSV file
    for row in reader:
        street_name = row[10].strip()
        so=row[11]
        cp = row[12]
        co = row[13]
        mesto = row[8]
        psc = row[15]

        if street_name == "":
            street_name = mesto

        if street_name == street_in:
            writer.writerow([street_name, so, cp, co, mesto, psc])  # Write the modified row to the output CSV file

# Remove the downloaded files
remove_file(input_file)
remove_file(zip_file_name)
remove_file(csv_file_name)
remove_file(file_name)
