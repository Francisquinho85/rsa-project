from time import sleep
import paho.mqtt.client as mqtt
import json
from simulator.Messages.event import event
import time


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

    def updateEvent(self, causeCode, subCauseCode):
        self.denm["situation"]["eventType"]["causeCode"] = causeCode
        self.denm["situation"]["eventType"]["subCauseCode"] = subCauseCode

    def on_connect(self, client, userdata, flags, rc):
        self.mqttc.subscribe([("vanetza/out/cam", 0), ("vanetza/out/denm", 0)])

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode())
        if(msg.topic == "vanetza/out/denm" and message["fields"]["denm"]
           ["situation"]["eventType"]["causeCode"] == event["batteryStatus"]):
            print("Sending Park status " + self.name)
            if(self.freeCharges > 0):
                self.updateEvent(event["parkStatus"],
                                 event["parkWithChargerPlace"])
            elif(self.freeSlots > 0):
                self.updateEvent(event["parkStatus"],
                                 event["parkWithNormalPlace"])
            else:
                self.updateEvent(event["parkStatus"],
                                 event["parkFull"])
            self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
        # Reserve charger slot confirmation or cancel
        if(msg.topic == "vanetza/out/denm" and message["fields"]["denm"]
           ["situation"]["eventType"]["subCauseCode"] == self.id):
            if(message["fields"]["denm"]
               ["situation"]["eventType"]["causeCode"] == event["reserveSlotCharger"]):
                if(self.freeCharges > 0):
                    self.updateEvent(event["confirmSlot"], message["fields"]
                                     ["denm"]["management"]["actionID"]["originatingStationID"])
                    self.freeCharges -= 1
                    self.freeSlots -= 1
                    for c in range(self.charges):
                        if(self.carList[c] == None):
                            self.carList[c] = message["fields"]
                            ["denm"]["management"]["actionID"]["originatingStationID"]
                    print(self.name + " Confirming slot charger")
                elif(self.freeCharges == 0):
                    self.updateEvent(event["cancelSlot"], message["fields"]
                                     ["denm"]["management"]["actionID"]["originatingStationID"])
                    print(self.name + " Canceling slot charger")
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
            # Reserve normal slot confirmation or cancel
            if(message["fields"]["denm"]
               ["situation"]["eventType"]["causeCode"] == event["reserveSlotNormal"]):
                print("RSU Confirming slot normal")
                if(self.freeSlots > 0):
                    self.updateEvent(event["confirmSlot"], message["fields"]
                                     ["denm"]["management"]["actionID"]["originatingStationID"])
                    self.freeSlots -= 1
                    for c in range(self.charges, self.slots):
                        if(self.carList[c] == None):
                            self.carList[c] = message["fields"]
                            ["denm"]["management"]["actionID"]["originatingStationID"]
                elif(self.freeSlots == 0):
                    self.updateEvent(event["cancelSlot"], message["fields"]
                                     ["denm"]["management"]["actionID"]["originatingStationID"])
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))

    def run(self, sio, sid):
        self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
        while True:
            time.sleep(1)
