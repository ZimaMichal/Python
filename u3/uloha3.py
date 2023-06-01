import requests
import zipfile
import csv
import os 

# Setting dictionary path
path_in = input("Zadejte cestu pro uložení souborů:")
os.chdir(path_in)

url = "https://www.cuzk.cz/CUZK/media/CiselnikyISUI/UI_OBEC/UI_OBEC.zip?ext=.zip"
zip_file_name = "RUIAN_OBCE.ZIP"  # ZIP file name
csv_file_name = "UI_OBEC.csv"  # CSV file name

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:

    # Save the ZIP file to disk
    with open(zip_file_name, "wb") as file:
        file.write(response.content)
    print("ZIP file downloaded successfully.")

else:
    print("Failed to download the ZIP file.")

# Unzip the file
with zipfile.ZipFile(zip_file_name, "r") as zip_ref:
    zip_ref.extractall()
print("ZIP file extracted successfully.")

obce_kody = {}  # Empty dictionary to store codes and names 

# Read the CSV file and save the first and second fields to the dictionary
with open(csv_file_name, 'r') as csv_file:
    reader = csv.reader(csv_file, delimiter=';')
    next(reader)  # Skip the header row
    for row in reader:
        obce_kody[row[1]] = row[0]

print("Data saved to the dictionary successfully.")

# Prompt the user for name of the city
city_in = input("Zadejte název obce: ")

if city_in in obce_kody:
    # Prompt the user for name of the street
    street_in = input("Zadejte název ulice (pokud neni, zadejte znovu název obec): ")

    # Retrieve the code for the entered city
    code_out = obce_kody.get(city_in)

    print("Kód pro obec", city_in, "je", code_out)
    print("Stahuji příslušný CSV soubor")
    
    url = f"https://vdp.cuzk.cz/vymenny_format/csv/20230430_OB_{code_out}_ADR.csv.zip"
    file_name = f"20230430_OB_{code_out}_ADR.csv.ZIP"  # Specify the desired file path

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the file to disk
        with open(file_name, "wb") as file:
            file.write(response.content)
        print("File downloaded successfully.")
    else:
        print("Failed to download the file.")

    # Unzip the file
    with zipfile.ZipFile(file_name, "r") as zip_ref:
        zip_ref.extractall()
    print("File extracted successfully.")

    input_file = f"20230430_OB_{code_out}_ADR.csv"
    output_file = f"adresni_mista_{city_in}_{street_in}.csv"
    eror=0
    # Open the input and output CSV files
    with open(input_file, 'r') as input_csv, open(output_file, 'w', newline='') as output_csv:
        # Create CSV reader and writer objects
        reader = csv.reader(input_csv, delimiter=';')
        writer = csv.writer(output_csv, delimiter=';')

        # Process each row in the input CSV file
        for row in reader:
            ulice = row[10]  
            cp = row[12]
            co = row[13]
            mesto = row[8]
            psc = row[15]

            if ulice == "":
                ulice=mesto
            
            if ulice == street_in:
                writer.writerow([ulice, 'č.p.', cp, co, mesto, psc])  # Write the modified row to the output CSV file
                eror=1

    #Error - street don´t exist in the list
    if eror==0:

        print("Ulice nenalezena.")

    # Remove the useless downloaded files 
    os.remove(input_file)
    os.remove(zip_file_name)
    os.remove(csv_file_name)
    os.remove(file_name)

#Error - city don´t exist in list
else:
    print("Kód pro obec nenalezen.")
    # Remove the useless downloaded files
    os.remove(zip_file_name)
    os.remove(csv_file_name)
