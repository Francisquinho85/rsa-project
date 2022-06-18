from time import sleep
import paho.mqtt.client as mqtt
import json
from simulator.Messages.event import event
import time


class Park:
    def __init__(self, slots, charges, latitude, longitude, cam, denm, ip, name):
        self.slots = slots
        self.charges = charges
        self.freeCharges = charges
        self.freeSlots = slots
        self.latitude = latitude
        self.longitude = longitude
        self.carList = []
        self.cam = cam
        self.denm = denm
        self.ip = ip
        self.name = name
        self.mqttc = mqtt.Client()
        self.mqttc.connect(ip)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.loop_start()

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
        a = 0
        message = json.loads(msg.payload.decode())
        if(msg.topic == "vanetza/out/denm" and message["fields"]["denm"]
           ["situation"]["eventType"]["causeCode"] == event["batteryStatus"]):
            # print("park receive denm")
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
        # if(msg.topic == "vanetza/out/cam"):
        #     print("park receive cam")
            # print(msg.payload["fields"]["denm"]["situation"]["eventType"]["causeCode"])
            # print(json.loads(msg.payload.decode())["fields"]["denm"]
            #       ["situation"]["eventType"]["causeCode"])

    def run(self, sio, sid):
        while True:
            self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
            time.sleep(1)
