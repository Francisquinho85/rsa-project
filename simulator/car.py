from threading import Thread
from time import sleep
from xml.dom.expatbuilder import theDOMImplementation
import paho.mqtt.client as mqtt
import json
import time

from pyrsistent import s
from simulator.Messages.event import event
from random import randint


class Car:
    def __init__(self, cam, denm, ip, name):
        self.battery = 0
        self.latitude = 0
        self.longitude = 0
        self.cam = cam
        self.denm = denm
        self.ip = ip
        self.name = name
        self.location = 0
        self.battery = 0
        self.mqttc = mqtt.Client()
        self.mqttc.connect(ip)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.loop_start()

    def updateLocation(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.denm["management"]["eventPosition"]["latitude"] = self.latitude
        self.denm["management"]["eventPosition"]["longitude"] = self.longitude
        self.cam["latitude"] = self.latitude
        self.cam["longitude"] = self.longitude

    def sendLocation(self):
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "battery": self.battery
        }

    def updateEvent(self, causeCode, subCauseCode):
        self.denm["situation"]["eventType"]["causeCode"] = causeCode
        self.denm["situation"]["eventType"]["subCauseCode"] = 10000

    def on_connect(self, client, userdata, flags, rc):
        self.mqttc.subscribe([("vanetza/out/cam", 0), ("vanetza/out/denm", 0)])

    def on_message(self, client, userdata, msg):
        a = 0
        message = json.loads(msg.payload.decode())
        if(msg.topic == "vanetza/out/denm" and message["fields"]["denm"]
           ["situation"]["eventType"]["causeCode"] == event["parkStatus"]):
            if(message["fields"]["denm"]
               ["situation"]["eventType"]["causeCode"] == event["parkWithChargerPlace"]):
                a = 0
            elif(message["fields"]["denm"]
                 ["situation"]["eventType"]["causeCode"] == event["parkWithNormalPlace"]):
                a = 0

             # if(msg.topic == "vanetza/out/denm"):
             #     # print("car receive denm")
             # if(msg.topic == "vanetza/out/cam"):
             #     # print("car receive cam")
             # print(msg.payload)

    # def needToCharge(self):

    def run(self, sio, sid, coords_json):
        while True:
            self.location += 1
            self.battery -= randint(0, 3)
            if(self.location > 135):
                self.location -= 136
            self.updateLocation((float)(coords_json[str(self.location)]["latitude"]), (float)(
                coords_json[str(self.location)]["longitude"]))
            self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
            if(self.battery <= 25 and self.battery % 5 == 0):
                self.updateEvent(event["batteryStatus"], event["battery0_25"])
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
            result = sio.call(
                'send_coords', self.sendLocation(), to=sid)
            time.sleep(1)
