import copy
from random import randint
from time import sleep
import json

from simulator.car import Car
from simulator.park import Park


# The callback for when a PUBLISH message is received from the server.
def main(sid, sio):
    print(sid)
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
               copy.deepcopy(denm_json), "192.168.98.20", "obu1")

    carLocation = randint(0, 135)
    car1.location = carLocation
    car1.updateLocation((float)(coords_json[str(carLocation)]["latitude"]),
                        (float)(coords_json[str(carLocation)]["longitude"]))
    print((float)(coords_json["0"]["latitude"]))
    park1 = Park(3, 2, 4, 4, copy.deepcopy(cam_json),
                 copy.deepcopy(denm_json), "192.168.98.10")
    park1.updateLocation()

    while True:

        print(car1.location)
        car1.updateLocation(coords_json)
        ret1 = car1.mqttc.publish("vanetza/in/cam", json.dumps(car1.cam))
        result = sio.call(
            'send_coords', car1.sendLocation(), to=sid)
        # car1.updateLocation((float)(coords_json[i]["latitude"]),
        #                     (float)(coords_json[i]["longitude"]))
        # ret2 = park1.mqttc.publish("vanetza/in/cam", json.dumps(park1.cam))
        sleep(1)

    mqttc.disconnect()
