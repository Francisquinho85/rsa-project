import imp
import json


coords_file = open("coords.json", "r")
coords_json = json.load(coords_file)
coords_file.close()
parkLatitude = 40.63774
parkLongitude = -8.65824
for i in coords_json:
    if((float)(coords_json[i]["latitude"]) == parkLatitude and (float)(coords_json[i]["longitude"]) == parkLongitude):
        print((int)(i))
