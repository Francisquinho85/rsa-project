import json

coords_file = open("coords.json", "r")
coords_json = json.load(coords_file)
coords_file.close()

for i in coords_json:
    print(coords_json[i]["latitude"])
