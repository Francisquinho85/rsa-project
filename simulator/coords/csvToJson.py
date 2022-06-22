import csv
import json

data = {}

with open("coords.csv", encoding='utf-8') as csvf:
    csvReader = csv.DictReader(csvf)

    cont = 0
    for rows in csvReader:
        data[str(cont)] = rows
        cont += 1

with open("coords.json", 'w', encoding='utf-8') as jsonf:
    json.dump(data, jsonf, indent=4)
