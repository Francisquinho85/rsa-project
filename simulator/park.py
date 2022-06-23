import paho.mqtt.client as mqtt
import json
import time

from simulator.messages.event import event
from simulator.utils import *

class Park:
    def __init__(self, slots, charges, latitude, longitude, cam, denm, ip, name, id, sid, sio):
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
        self.sid = sid
        self.sio = sio

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
        if(msg.topic == "vanetza/out/denm" and getCauseCode(message) == event["batteryStatus"] and getType(message) == 5):
            # result = self.sio.call('send_message', self.sendMessage("Receive denm batteryStatus to obu" + str(getId(message))), to=self.sid)
            print("Sending Park status " , self.name , " free " , self.freeCharges  , " slots " , self.freeSlots , " " , self.carList)
            if(self.freeCharges > 0):
                self.updateEvent(event["parkStatus"], event["parkWithChargerPlace"])
                result = self.sio.call('send_message', self.sendMessage("DENM - parkStatus(" + str(event["parkStatus"]) + ") : parkWithChargerPlace(" + str(event["parkWithChargerPlace"])+ ")"), to=self.sid)
            elif(self.freeSlots > 0):
                self.updateEvent(event["parkStatus"], event["parkWithNormalPlace"])
                result = self.sio.call('send_message', self.sendMessage("DENM - parkStatus(" + str(event["parkStatus"]) + ") : parkWithNormalPlace(" + str(event["parkWithNormalPlace"])+ ")"), to=self.sid)
            else:
                self.updateEvent(event["parkStatus"], event["parkFull"])
                result = self.sio.call('send_message', self.sendMessage("DENM - parkStatus(" + str(event["parkStatus"]) + ") : parkFull(" + str(event["parkFull"])+ ")"), to=self.sid)
            self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
        # Reserve charger slot confirmation or cancel
        if(msg.topic == "vanetza/out/denm" and getSubCauseCode(message) == self.id and getType(message) == 5):
            
            if(getCauseCode(message) == event["reserveSlotCharger"]):
                # result = self.sio.call('send_message', self.sendMessage("Receive denm reserveSlotCharger to obu" + str(getId(message))), to=self.sid)
                if(self.freeCharges > 0):
                    self.updateEvent(event["confirmSlot"], getId(message))
                    self.freeCharges -= 1
                    self.freeSlots -= 1
                    for c in range(self.charges):
                        if(self.carList[c] == None):
                            self.carList[c] = getId(message)
                            break
                    result = self.sio.call('send_message', self.sendMessage("DENM - confirmSlot(" + str(event["confirmSlot"]) + ") : obuId(" + str(getId(message)) + ")"), to=self.sid)
                    print(self.name + " Confirming slot charger")
                elif(self.freeCharges == 0):
                    self.updateEvent(event["cancelSlot"], getId(message))
                    print(self.name + " Canceling slot charger")
                    result = self.sio.call('send_message', self.sendMessage("DENM - cancelSlot(" + str(event["cancelSlot"]) + ") : obuId(" + str(getId(message)) + ")"), to=self.sid)
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
            # Reserve normal slot confirmation or cancel
            
            if(getCauseCode(message) == event["reserveSlotNormal"]):
                # result = self.sio.call('send_message', self.sendMessage("Receive denm reserveSlotNormal to obu" + str(getId(message))), to=self.sid)
                print("RSU Confirming slot normal")
                if(self.freeSlots > 0):
                    self.updateEvent(event["confirmSlot"],getId(message))
                    self.freeSlots -= 1
                    for c in range(self.charges, self.slots):
                        if(self.carList[c] == None):
                            self.carList[c] = getId(message)
                            break
                    result = self.sio.call('send_message', self.sendMessage("DENM - confirmSlot(" + str(event["confirmSlot"]) + ") : obuId(" + str(getId(message)) + ")"), to=self.sid)
                elif(self.freeSlots == 0):
                    self.updateEvent(event["cancelSlot"], getId(message))
                    result = self.sio.call('send_message', self.sendMessage("DENM - cancelSlot(" + str(event["cancelSlot"]) + ") : obuId(" + str(getId(message)) + ")"), to=self.sid)
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

            if(getCauseCode(message) == event["cancelSlot"]):
                for c in range(len(self.carList)):
                    if(self.carList[c] == getId(message)):
                        if(self.carList[self.slots-1] == self.carList[c]):
                            self.carList[c] = None
                            self.freeSlots += 1
                        elif(self.carList[self.slots-1] != None):
                            self.carList[c] = self.carList[self.slots-1]
                            self.freeSlots += 1
                            self.carList[self.slots-1] = None
                        else:
                            self.freeCharges += 1
                            self.freeSlots += 1
                            self.carList[c] = None
                        result = self.sio.call('reserve_slot', self.sendSlots(self.carList[c], c, 0), to=self.sid)

    def sendSlots(self, id, slot, changePlace):
        return{
            "rsuName": self.name,
            "obuName": "obu" + (str)(id),
            "slot": slot,
            "changePlace": changePlace
        }

    def sendMessage(self, message):
        return {
            "name": self.name,
            "message": message
        }

    def run(self):
        self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
        saveCarList = self.carList.copy()
        while True:
            for c in range(len(self.carList)):
                changePlace = 0
                if(saveCarList[c] != self.carList[c]):
                    if(self.carList[c] == saveCarList[self.slots-1] and self.carList[c]!= None):
                        print("change to charger car:", self.carList[c])
                        self.updateEvent(event["changeToCharger"], self.carList[c])
                        self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                        changePlace = 1
                        result = self.sio.call('send_message', self.sendMessage("DENM - changeToCharger(" + str(event["changeToCharger"]) + ") : obuId(" + str(self.carList[c]) + ")"), to=self.sid)
                    result = self.sio.call('reserve_slot', self.sendSlots(self.carList[c], c, changePlace), to=self.sid)
                    saveCarList = self.carList.copy()
                    print(self.name , " " , self.carList) # print(self.carList)
            # print(self.name , " " , self.carList)
            # self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
            time.sleep(0.2)
