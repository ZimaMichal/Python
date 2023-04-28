import re

data_soubor = open('FinalText.txt',encoding="utf8")

text = data_soubor.read()

data_soubor.close()

cisla=re.findall(r'[\d]+',text) #vytvoří list čísel s datový typem string
cisla_int=list(map(int, cisla)) #převod typu string na int
print(sum(cisla_int)) #výpis výsledné sumy
