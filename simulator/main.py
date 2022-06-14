import copy
from random import randint
from time import sleep
import json

from simulator.car import Car
from simulator.park import Park
from simulator.Messages.event import event


# The callback for when a PUBLISH message is received from the server.
def main(sid, sio):
    print(sid)
    denm_file = open("simulator/Messages/denm.json", "r")
    denm_json = json.load(denm_file)
    denm_file.close()
    cam_file = open("simulator/Messages/cam.json", "r")
    cam_json = json.load(cam_file)
    cam_file.close()
    coords_file = open("simulator/coords.json", "r")
    coords_json = json.load(coords_file)
    coords_file.close()

    obus = []

    obu1 = Car(copy.deepcopy(cam_json),
               copy.deepcopy(denm_json), "192.168.98.20", "obu1")
    obu1.location = randint(0, 135)
    obu1.updateLocation((float)(coords_json[str(obu1.location)]["latitude"]), (float)(
        coords_json[str(obu1.location)]["longitude"]))
    obu1.battery = randint(30, 100)
    obus.append(obu1)

    obu2 = Car(copy.deepcopy(cam_json),
               copy.deepcopy(denm_json), "192.168.98.21", "obu2")
    obu2.location = randint(0, 135)
    obu2.updateLocation((float)(coords_json[str(obu2.location)]["latitude"]), (float)(
        coords_json[str(obu2.location)]["longitude"]))
    obu2.battery = randint(30, 100)
    obus.append(obu2)

    obu3 = Car(copy.deepcopy(cam_json),
               copy.deepcopy(denm_json), "192.168.98.22", "obu3")
    obu3.location = randint(0, 135)
    obu3.updateLocation((float)(coords_json[str(obu3.location)]["latitude"]), (float)(
        coords_json[str(obu3.location)]["longitude"]))
    obu3.battery = randint(30, 100)
    obus.append(obu3)

    obu4 = Car(copy.deepcopy(cam_json),
               copy.deepcopy(denm_json), "192.168.98.23", "obu4")
    obu4.location = randint(0, 135)
    obu4.updateLocation((float)(coords_json[str(obu4.location)]["latitude"]), (float)(
        coords_json[str(obu4.location)]["longitude"]))
    obu4.battery = randint(30, 100)
    obus.append(obu4)

    obu5 = Car(copy.deepcopy(cam_json),
               copy.deepcopy(denm_json), "192.168.98.24", "obu5")
    obu5.location = randint(0, 135)
    obu5.updateLocation((float)(coords_json[str(obu5.location)]["latitude"]), (float)(
        coords_json[str(obu5.location)]["longitude"]))
    obu5.battery = randint(30, 100)
    obus.append(obu5)

    obu6 = Car(copy.deepcopy(cam_json),
               copy.deepcopy(denm_json), "192.168.98.25", "obu6")
    obu6.location = randint(0, 135)
    obu6.updateLocation((float)(coords_json[str(obu6.location)]["latitude"]), (float)(
        coords_json[str(obu6.location)]["longitude"]))
    obu6.battery = randint(30, 100)
    obus.append(obu6)

    rsus = []

    rsu1 = Park(3, 2, 4, 4, copy.deepcopy(cam_json),
                copy.deepcopy(denm_json), "192.168.98.10", "rsu1")
    rsu1.updateLocation()
    rsus.append(rsu1)

    rsu2 = Park(3, 2, 4, 4, copy.deepcopy(cam_json),
                copy.deepcopy(denm_json), "192.168.98.11", "rsu2")
    rsu2.updateLocation()
    rsus.append(rsu2)

    while True:
        for obu in obus:
            obu.location += 1
            obu.battery -= randint(0, 3)
            if(obu.location > 135):
                obu.location -= 136
            obu.updateLocation((float)(coords_json[str(obu.location)]["latitude"]), (float)(
                coords_json[str(obu.location)]["longitude"]))
            obu.mqttc.publish("vanetza/in/cam", json.dumps(obu.cam))
            if(obu.battery <= 25):
                obu.denm["situation"]["eventType"]["causeCode"] = event["batteryStatus"]
                obu.denm["situation"]["eventType"]["causeCode"] = event["battery0_25"]
                obu.mqttc.publish("vanetza/in/denm", json.dumps(obu.denm))
            result = sio.call(
                'send_coords', obu.sendLocation(), to=sid)
            # obu.updateLocation((float)(coords_json[i]["latitude"]),
            #                     (float)(coords_json[i]["longitude"]))
            # ret2 = park1.mqttc.publish("vanetza/in/cam", json.dumps(park1.cam))
        sleep(1)

    mqttc.disconnect()
