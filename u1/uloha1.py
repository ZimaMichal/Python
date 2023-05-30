import re

# Import textového souboru
with open('FinalText.txt', 'r', encoding="utf8") as file:
    text = file.read()

cisla=re.findall(r'[\d]+',text) #vytvoří list čísel s datový typem string
cisla_int=list(map(int, cisla)) #převod typu string na int
print(sum(cisla_int)) #výpis výsledné sumy
