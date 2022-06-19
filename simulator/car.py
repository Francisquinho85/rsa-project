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
        self.slotReserved = False
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
                    ["situation"]["eventType"]["causeCode"] == event["parkStatus"] and not self.slotReserved):
                if(message["fields"]["denm"]
                        ["situation"]["eventType"]["subCauseCode"] == event["parkWithChargerPlace"]):
                    print("Reserving Charger slot")
                    self.updateEvent(event["reserveSlotCharger"], message["fields"]
                                     ["denm"]["management"]["actionID"]["originatingStationID"])
                    self.mqttc.publish("vanetza/in/denm",
                                       json.dumps(self.denm))
                    self.slotReserved = True
                elif(message["fields"]["denm"]
                        ["situation"]["eventType"]["subCauseCode"] == event["parkWithNormalPlace"]):
                    print("Reserving Normal slot")
                    self.updateEvent(event["reserveSlotNormal"], message["fields"]
                                     ["denm"]["management"]["actionID"]["originatingStationID"])
                    self.mqttc.publish("vanetza/in/denm",
                                       json.dumps(self.denm))
                    self.slotReserved = True
            # Receive park confirm or cancel
            print(message["fields"]["denm"]
                    ["situation"]["eventType"]["subCauseCode"])
            if(message["fields"]["denm"]
                    ["situation"]["eventType"]["subCauseCode"] == self.id):
                print("Receive park confirm or cancel")
                if(message["fields"]["denm"]
                        ["situation"]["eventType"]["causeCode"] == event["confirmSlot"]):
                    print("Slot Confirmed for " + self.name)
                    self.wantToCharge = False
                    self.slotReserved = False
                    self.parkLatitude = self.denm["management"]["eventPosition"]["latitude"]
                    self.parkLongitude = self.denm["management"]["eventPosition"]["longitude"]
                if(message["fields"]["denm"]
                        ["situation"]["eventType"]["causeCode"] == event["cancelSlot"]):
                    print("Slot Canceled for " + self.name)
                    self.slotReserved = False
                    a = 0  # TODO normal life

    def getParkLocation(self, coords_json):
        for i in coords_json:
            if(coords_json[i]["latitude"] == self.parkLatitude and coords_json[i]["longitude"] == self.parkLongitude):
                return i

    def goToThePark(self, sio, sid, coords_json):
        parkLocation = self.getParkLocation(coords_json)
        reverse = False
        print("Going to the park " + self.name)
        #Check which direction is faster
        print(parkLocation, self.location)

        if(parkLocation > self.location):
            if((parkLocation - self.location) < (self.location + (135 - parkLocation))):
                reverse = False
            else:    
                reverse = True
        else:
            if((self.location - parkLocation) < (parkLocation + (135 - self.location))):
                reverse = True
            else:
                reverse = False
        
        while True:
            #Check if arrived to the park
            if(self.location == parkLocation):
                break

            #Drive to park in the fastest direction
            if(reverse):
                self.location -= 1
            else:
                self.location += 1
            
            #Decrease battery percentage
            self.battery -= randint(0, 3)

            #Check if is in the position limits
            if(self.location > 135):
                self.location = 0
            elif(self.location < 0):
                self.location = 135
            
            #Update Coordinates
            self.updateLocation((float)(coords_json[str(self.location)]["latitude"]), (float)(
                coords_json[str(self.location)]["longitude"]))
            self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
            
            #Send new coordinates to frontend
            result = sio.call(
                'send_coords', self.sendLocation(), to=sid)
            time.sleep(1)

    def enterThePark(self, sio, sid, coords_json, desiredBattery):
        isCharged = False
        print("Entered the park " + self.name)
        while True:
            if(self.battery == desiredBattery):
                break
            self.battery += 10
            if self.battery >= 100:
                self.battery = 100
            time.sleep(1)
            result = sio.call('enter_park', self.sendLocation(), to=sid)

    def leaveThePark(self, sio, sid, coords_json):
        print("Leaving the park " + self.name)
        self.parkLatitude = 0
        self.parkLongitude = 0
        result = sio.call(
                'send_coords', self.sendLocation(), to=sid)

    def run(self, sio, sid, coords_json):
        self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
        while True:
            if(self.parkLatitude != 0):
                self.goToThePark(sio, sid, coords_json)
                self.enterThePark(sio, sid, coords_json, 100)
                self.leaveThePark(sio, sid, coords_json)
            self.location += 1
            self.battery -= randint(0, 3)
            if(self.location > 135):
                self.location = 0
            self.updateLocation((float)(coords_json[str(self.location)]["latitude"]), (float)(
                coords_json[str(self.location)]["longitude"]))
            #self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
            if(self.battery <= 25 and not self.wantToCharge):
                print("I want to charge " + self.name)
                self.wantToCharge = True
                self.updateEvent(event["batteryStatus"], event["battery0_25"])
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
            result = sio.call(
                'send_coords', self.sendLocation(), to=sid)
            time.sleep(1)
