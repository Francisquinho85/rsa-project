import paho.mqtt.client as mqtt
import json
import time

from simulator.messages.event import event
from simulator.utils import *

class Park:
    def __init__(self, slots, charges, latitude, longitude, cam, denm, ip, name, id):
        self.slots = slots
        self.charges = charges
        self.freeCharges = charges
        self.freeSlots = slots
        self.latitude = latitude
        self.longitude = longitude
        self.carList = []
        for i in range(slots):
            self.carList.append(None)
        self.cam = cam
        self.denm = denm
        self.ip = ip
        self.id = id
        self.name = name
        self.mqttc = mqtt.Client()
        self.mqttc.connect(ip)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.loop_start()
        self.cam["stationID"] = id
        self.cam["stationType"] = 15
        self.denm["management"]["actionID"]["originatingStationID"] = id
        self.denm["management"]["stationType"] = 15

    def updateLocation(self):
        self.denm["management"]["eventPosition"]["latitude"] = self.latitude
        self.denm["management"]["eventPosition"]["longitude"] = self.longitude
        self.cam["latitude"] = self.latitude
        self.cam["longitude"] = self.longitude
        print(self.latitude, " ", self.longitude)

    def updateEvent(self, causeCode, subCauseCode):
        self.denm["situation"]["eventType"]["causeCode"] = causeCode
        self.denm["situation"]["eventType"]["subCauseCode"] = subCauseCode

    def on_connect(self, client, userdata, flags, rc):
        self.mqttc.subscribe([("vanetza/out/cam", 0), ("vanetza/out/denm", 0)])

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode())
        if(msg.topic == "vanetza/out/denm" and getCauseCode(message) == event["batteryStatus"]):
            print("Sending Park status " , self.name , " free " , self.freeCharges  , " slots " , self.freeSlots , " " , self.carList)
            if(self.freeCharges > 0):
                self.updateEvent(event["parkStatus"], event["parkWithChargerPlace"])
            elif(self.freeSlots > 0):
                self.updateEvent(event["parkStatus"], event["parkWithNormalPlace"])
            else:
                self.updateEvent(event["parkStatus"], event["parkFull"])
            self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
        # Reserve charger slot confirmation or cancel
        if(msg.topic == "vanetza/out/denm" and getSubCauseCode(message) == self.id):
            if(getCauseCode(message) == event["reserveSlotCharger"]):
                if(self.freeCharges > 0):
                    self.updateEvent(event["confirmSlot"], getId(message))
                    self.freeCharges -= 1
                    self.freeSlots -= 1
                    for c in range(self.charges):
                        if(self.carList[c] == None):
                            self.carList[c] = getId(message)
                            break
                    print(self.name + " Confirming slot charger")
                elif(self.freeCharges == 0):
                    self.updateEvent(event["cancelSlot"], getId(message))
                    print(self.name + " Canceling slot charger")
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
            # Reserve normal slot confirmation or cancel
            if(getCauseCode(message) == event["reserveSlotNormal"]):
                print("RSU Confirming slot normal")
                if(self.freeSlots > 0):
                    self.updateEvent(event["confirmSlot"],getId(message))
                    self.freeSlots -= 1
                    for c in range(self.charges, self.slots):
                        if(self.carList[c] == None):
                            self.carList[c] = getId(message)
                            break
                elif(self.freeSlots == 0):
                    self.updateEvent(event["cancelSlot"], getId(message))
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
            if(getCauseCode(message) == event["exitPark"]):
                print("Car exit park")
                for c in range(len(self.carList)):
                    if(self.carList[c] == getId(message)):
                        if(self.carList[self.slots-1] != None):
                            self.carList[c] = self.carList[self.slots-1]
                            self.freeSlots += 1
                            self.carList[self.slots-1] = None
                        else:
                            self.freeCharges += 1
                            self.freeSlots += 1
                            self.carList[c] = None


    def sendSlots(self, id, slot, changePlace):
        return{
            "rsuName": self.name,
            "obuName": "obu" + (str)(id),
            "slot": slot,
            "changePlace": changePlace
        }

    def run(self, sio, sid):
        self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
        saveCarList = self.carList.copy()
        while True:
            for c in range(len(self.carList)):
                changePlace = 0
                if(saveCarList[c] != self.carList[c]):
                    if(self.carList[c] == saveCarList[self.slots-1]):
                        print("change to charger car:", self.carList[c])
                        self.updateEvent(event["changeToCharger"], self.carList[c])
                        self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                        changePlace = 1
                    result = sio.call('reserve_slot', self.sendSlots(self.carList[c], c, changePlace), to=sid)
                    saveCarList = self.carList.copy()
                    # print(self.carList)
            print(self.name , " " , self.carList)
            time.sleep(0.1)
