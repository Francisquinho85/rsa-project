from threading import Thread
from time import sleep
from tokenize import Triple
from xml.dom.expatbuilder import theDOMImplementation
import paho.mqtt.client as mqtt
import json
import time

from pyrsistent import s
from simulator.Messages.event import event
from random import randint


class Car:
    def __init__(self, cam, denm, ip, name, id):
        self.battery = 0
        self.latitude = 0
        self.longitude = 0
        self.cam = cam
        self.denm = denm
        self.ip = ip
        self.id = id
        self.name = name
        self.location = 0
        self.battery = 0
        self.wantToCharge = False
        self.parkLatitude = 0
        self.parkLongitude = 0
        self.mqttc = mqtt.Client()
        self.mqttc.connect(ip)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.loop_start()
        self.cam["stationID"] = id
        self.cam["stationType"] = 5
        self.denm["management"]["actionID"]["originatingStationID"] = id
        self.denm["management"]["stationType"] = 5

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
        self.denm["situation"]["eventType"]["subCauseCode"] = subCauseCode

    def on_connect(self, client, userdata, flags, rc):
        self.mqttc.subscribe([("vanetza/out/cam", 0), ("vanetza/out/denm", 0)])

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode())
        if(msg.topic == "vanetza/out/denm" and self.wantToCharge):
            # Receive park status
            if(message["fields"]["denm"]
                    ["situation"]["eventType"]["causeCode"] == event["parkStatus"]):
                if(message["fields"]["denm"]
                        ["situation"]["eventType"]["subCauseCode"] == event["parkWithChargerPlace"]):
                    self.updateEvent(event["reserveSlot"], message["fields"]
                                     ["denm"]["management"]["actionID"]["originatingStationID"])
                    self.mqttc.publish("vanetza/in/denm",
                                       json.dumps(self.denm))
                elif(message["fields"]["denm"]
                        ["situation"]["eventType"]["subCauseCode"] == event["parkWithNormalPlace"]):
                    self.updateEvent(event["reserveSlot"], message["fields"]
                                     ["denm"]["management"]["actionID"]["originatingStationID"])
                    self.mqttc.publish("vanetza/in/denm",
                                       json.dumps(self.denm))
            # Receive park confirm or cancel
            if(message["fields"]["denm"]
                    ["situation"]["eventType"]["subCauseCode"] == self.id):
                if(message["fields"]["denm"]
                        ["situation"]["eventType"]["causeCode"] == event["confirmSLot"]):
                    self.parkLatitude = self.denm["management"]["eventPosition"]["latitude"]
                    self.parkLongitude = self.denm["management"]["eventPosition"]["longitude"]
                if(message["fields"]["denm"]
                        ["situation"]["eventType"]["causeCode"] == event["cancelSlot"]):
                    a = 0  # TODO normal life

    def getParkLocation(self, coords_json):
        for i in coords_json:
            if(coords_json[i]["latitude"] == self.parkLatitude and coords_json[i]["longitude"] == self.parkLongitude):
                return i

    def goToThePark(self, sio, sid, coords_json):
        parkLocation = self.getParkLocation(coords_json)
        abs(parkLocation - self.location) < abs(self.location - parkLocation)

        while True:
            self.location += 1
            self.battery -= randint(0, 3)
            if(self.location > 135):
                self.location -= 136
            self.updateLocation((float)(coords_json[str(self.location)]["latitude"]), (float)(
                coords_json[str(self.location)]["longitude"]))
            self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
            if(self.battery <= 25 and self.battery % 5 == 0):
                self.wantToCharge = True
                self.updateEvent(event["batteryStatus"], event["battery0_25"])
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
            result = sio.call(
                'send_coords', self.sendLocation(), to=sid)
            time.sleep(1)

    def run(self, sio, sid, coords_json):
        while True:
            if(self.parkLatitude != 0):
                self.goToThePark(sio, sid, coords_json)
            self.location += 1
            self.battery -= randint(0, 3)
            if(self.location > 135):
                self.location -= 136
            self.updateLocation((float)(coords_json[str(self.location)]["latitude"]), (float)(
                coords_json[str(self.location)]["longitude"]))
            self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
            if(self.battery <= 25 and self.battery % 5 == 0):
                self.wantToCharge = True
                self.updateEvent(event["batteryStatus"], event["battery0_25"])
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
            result = sio.call(
                'send_coords', self.sendLocation(), to=sid)
            time.sleep(1)
