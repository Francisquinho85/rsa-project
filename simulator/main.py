import copy
from time import sleep
import json

from car import Car
from park import Park


# The callback for when a PUBLISH message is received from the server.


denm_file = open("Mensages/denm.json", "r")
denm_json = json.load(denm_file)
denm_file.close()
cam_file = open("Mensages/cam.json", "r")
cam_json = json.load(cam_file)
cam_file.close()
coords_file = open("coords.json", "r")
coords_json = json.load(coords_file)
coords_file.close()

car1 = Car(copy.deepcopy(cam_json),
           copy.deepcopy(denm_json), "192.168.98.20")
car1.updateLocation((float)(coords_json["0"]["latitude"]),
                    (float)(coords_json["0"]["longitude"]))
print((float)(coords_json["0"]["latitude"]))
park1 = Park(3, 2, 4, 4, copy.deepcopy(cam_json),
             copy.deepcopy(denm_json), "192.168.98.10")
park1.updateLocation()

while True:
    for i in coords_json:
        ret1 = car1.mqttc.publish("vanetza/in/cam", json.dumps(car1.cam))
        car1.updateLocation((float)(coords_json[i]["latitude"]),
                            (float)(coords_json[i]["longitude"]))
        sleep(1)
    # ret2 = park1.mqttc.publish("vanetza/in/cam", json.dumps(park1.cam))

mqttc.disconnect()
