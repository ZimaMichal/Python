import re
from collections import Counter

# Import textového souboru
with open('FinalText.txt', 'r', encoding="utf8") as file:
    text = file.read()
    words = re.findall(r'\b\w+\b', text)

# Nalezení nejdelšího slova
longest_word = max(words, key=len)

# Vytvoření slovníku pro výskyt jednotlivých slov
word_counts = {}

# Nalezení četnosti jednotlivých slov
for word in words:
    if word in word_counts:
        word_counts[word] += 1
    else:
        word_counts[word] = 1
        
# Nalezení nejčastějšího slova
most_freq_word=[]
max_freq=0

for word, count in word_counts.items():
    if count > max_freq:
        most_freq_word=[word]
        max_freq=count
    elif count == max_freq:
        most_freq_word.append(word)
# Výsledky
print(f'Nejdelší slovo je slovo {longest_word}.')
print(f'Nečastější slovo je slovo',most_freq_word[0])