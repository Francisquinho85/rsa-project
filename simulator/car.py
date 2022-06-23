import paho.mqtt.client as mqtt
import json
import time
from random import randint

from simulator.messages.event import event
from simulator.utils import *


class Car:
    def __init__(self, coords_json, cam, denm, ip, name, id, sid, sio):
        self.coords_json = coords_json
        self.battery = 0
        self.latitude = 0
        self.longitude = 0
        self.cam = cam
        self.denm = denm
        self.ip = ip
        self.id = id
        self.name = name
        self.location = 0
        self.wantToCharge = False
        self.normalSlotReserved = False
        self.chargerSlotReserved = False
        self.parkLatitude = 0
        self.parkLongitude = 0
        self.parkId = None
        self.mqttc = mqtt.Client()
        self.mqttc.connect(ip)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.loop_start()
        self.cam["stationID"] = id
        self.cam["stationType"] = 5
        self.denm["management"]["actionID"]["originatingStationID"] = id
        self.denm["management"]["stationType"] = 5
        self.sid = sid
        self.sio = sio
        self.currentPark = None

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
            "battery": int(self.battery/10)
        }

    def sendPark(self):
        return {
            "obuName": self.name,
            "rsuName": "rsu" + (str)(self.parkId),
            "battery": int(self.battery/10)
        }

    def sendBattery(self):
        return {
            "obuName": self.name,
            "battery": int(self.battery/10)
        }

    def sendMessage(self, message):
        return {
            "name": self.name,
            "message": message
        }

    def updateEvent(self, causeCode, subCauseCode):
        self.denm["situation"]["eventType"]["causeCode"] = causeCode
        self.denm["situation"]["eventType"]["subCauseCode"] = subCauseCode

    def on_connect(self, client, userdata, flags, rc):
        self.mqttc.subscribe([("vanetza/out/cam", 0), ("vanetza/out/denm", 0)])

    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload.decode())
        if(msg.topic == "vanetza/out/denm" and self.wantToCharge and getType(message) == 15):
            # Receive park status
            if(getCauseCode(message) == event["parkStatus"] and not self.normalSlotReserved and not self.chargerSlotReserved):
                # result = self.sio.call('send_message', self.sendMessage("Receive denm parkStatus from rsu" + str(getId(message))), to=self.sid)
                if(getSubCauseCode(message) == event["parkWithChargerPlace"]):
                    print("Reserving Charger slot " + self.name)
                    self.updateEvent(event["reserveSlotCharger"], getId(message))
                    self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                    self.chargerSlotReserved = True
                    self.currentPark = self.getParkLocation(getLatitude(message), getLongitude(message))
                    result = self.sio.call('send_message', self.sendMessage("DENM - reserveSlotCharger(" + str(event["reserveSlotCharger"]) + ") : rsuId(" + str(getId(message)) + ")"), to=self.sid)
                elif(getSubCauseCode(message) == event["parkWithNormalPlace"]):
                    print("Reserving Normal slot " + self.name)
                    self.updateEvent(event["reserveSlotNormal"], getId(message))
                    self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                    self.normalSlotReserved = True
                    self.currentPark = self.getParkLocation(getLatitude(message), getLongitude(message))
                    result = self.sio.call('send_message', self.sendMessage("DENM - reserveSlotNormal(" + str(event["reserveSlotNormal"]) + ") : rsuId(" + str(getId(message)) + ")"), to=self.sid)
            
            elif(getCauseCode(message) == event["parkStatus"] and (self.normalSlotReserved or self.chargerSlotReserved)):
                newPark = self.getParkLocation(getLatitude(message), getLongitude(message))
                if(self.normalSlotReserved and getSubCauseCode(message) == event["parkWithChargerPlace"]):
                    print("Reserving Charger slot " + self.name)
                    self.currentPark = newPark
                    self.updateEvent(event["reserveSlotCharger"], getId(message))
                    self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                    self.chargerSlotReserved = True
                    self.normalSlotReserved = False
                    result = self.sio.call('send_message', self.sendMessage("DENM - reserveSlotCharger(" + str(event["reserveSlotCharger"]) + ") : rsuId(" + str(getId(message)) + ")"), to=self.sid)
                elif(self.getParkDistance(newPark) < self.getParkDistance(self.currentPark)):
                    if(getSubCauseCode(message) == event["parkWithChargerPlace"]):
                        print("Reserving Charger slot " + self.name)
                        self.currentPark = newPark
                        self.updateEvent(event["reserveSlotCharger"], getId(message))
                        self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                        self.chargerSlotReserved = True
                        self.normalSlotReserved = False
                        result = self.sio.call('send_message', self.sendMessage("DENM - reserveSlotCharger(" + str(event["reserveSlotCharger"]) + ") : rsuId(" + str(getId(message)) + ")"), to=self.sid)
                    elif(getSubCauseCode(message) == event["parkWithNormalPlace"] and not self.chargerSlotReserved):
                        print("Reserving Normal slot " + self.name)
                        self.currentPark = newPark
                        self.updateEvent(event["reserveSlotNormal"], getId(message))
                        self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                        self.chargerSlotReserved = False
                        self.normalSlotReserved = True
                        result = self.sio.call('send_message', self.sendMessage("DENM - reserveSlotNormal(" + str(event["reserveSlotNormal"]) + ") : rsuId(" + str(getId(message)) + ")"), to=self.sid)
            
            
            
            # Receive park confirm or cancel
            elif(getSubCauseCode(message) == self.id):
                print("Receive park confirm or cancel " + self.name)
                if(getCauseCode(message) == event["confirmSlot"]):
                    messagePark = self.getParkLocation(getLatitude(message), getLongitude(message))
                    if(messagePark == self.currentPark):
                        if(self.parkId == None):
                            print("Slot Confirmed for " + self.name)
                            # self.wantToCharge = False
                            self.parkLatitude = (float)(getLatitude(message))
                            self.parkLongitude = (float)(getLongitude(message))
                            self.parkId = getId(message)
                        else:
                            print("Slot Confirmed for " + self.name)
                            # self.wantToCharge = False
                            self.parkLatitude = (float)(getLatitude(message))
                            self.parkLongitude = (float)(getLongitude(message))
                            self.updateEvent(event["cancelSlot"], self.parkId)
                            self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                            result = self.sio.call('send_message', self.sendMessage("DENM - cancelSlot(" + str(event["cancelSlot"]) + ") : rsuId(" + str(self.parkId) + ")"), to=self.sid)
                            self.parkId = getId(message)
                    elif(messagePark != self.currentPark):
                        if(self.parkId == None):
                            print("Slot Confirmed for " + self.name)
                            self.parkLatitude = (float)(getLatitude(message))
                            self.parkLongitude = (float)(getLongitude(message))
                            self.parkId = getId(message)
                        else:
                            self.updateEvent(event["cancelSlot"], getId(message))
                            self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                            result = self.sio.call('send_message', self.sendMessage("DENM - cancelSlot(" + str(event["cancelSlot"]) + ") : rsuId(" + str(getId(message)) + ")"), to=self.sid)
                    # result = self.sio.call('send_message', self.sendMessage("Receive denm confirmSlot from rsu" + str(getId(message))), to=self.sid)
                
                elif(getCauseCode(message) == event["cancelSlot"]):
                    print("Slot Canceled for " + self.name)
                    self.chargerSlotReserved = False
                    self.normalSlotReserved = False
                    # result = self.sio.call('send_message', self.sendMessage("Receive denm cancelSlot from rsu"+ str(getId(message))), to=self.sid)
        
        if(msg.topic == "vanetza/out/denm" and getSubCauseCode(message) == self.id and getCauseCode(message) == event["changeToCharger"] and getType(message) == 15):
            print("Slot Change for " + self.name)
            # result = self.sio.call('send_message', self.sendMessage("Receive denm changeToCharger from rsu"+ str(getId(message))), to=self.sid)
            self.chargerSlotReserved = True
            self.normalSlotReserved = False           

    def getParkLocation(self, latitude, longitude):
        for i in self.coords_json:
            if((float)(self.coords_json[i]["latitude"]) == round(latitude, 5) and (float)(self.coords_json[i]["longitude"]) == round(longitude, 5)):
                return (int)(i)

    def getParkDistance(self, parkLocation):
        if(parkLocation > self.location):
            distance1 = parkLocation - self.location
            distance2 = self.location + (135 - parkLocation)
        else:
            distance1 = self.location - parkLocation
            distance2 = parkLocation + (135 - self.location)
        if(distance1<distance2):
            return distance1
        return distance2

    def goToThePark(self):
        parkLocation = self.getParkLocation(self.parkLatitude, self.parkLongitude)
        reverse = False
        print("Going to the park " + self.name)
        # Check which direction is faster
        # result = self.sio.call('send_message', self.sendMessage("Going to the park"), to=self.sid)
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

        counter = 0 
        while True:
            
            if(counter%5 == 0):
                self.updateEvent(event["batteryStatus"], event["battery0_25"])
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                result = self.sio.call('send_message', self.sendMessage("DENM - batteryStatus(" + str(event["batteryStatus"]) + ") : battery0_25(" + str(event["battery0_25"])+ ")"), to=self.sid)
                counter = 0

            # Check if arrived to the park
            if(parkLocation != self.getParkLocation(self.parkLatitude, self.parkLongitude)):
                break

            if(self.location == parkLocation):
                break

            # Drive to park in the fastest direction
            if(reverse):
                self.location -= 1
            else:
                self.location += 1

            # Decrease battery percentage
            self.battery -= randint(0, 5)

            # Check if is in the position limits
            if(self.location > 135):
                self.location = 0
            elif(self.location < 0):
                self.location = 135

            # Update Coordinates
            self.updateLocation((float)(self.coords_json[str(self.location)]["latitude"]), (float)(self.coords_json[str(self.location)]["longitude"]))
            # self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))

            # Send new coordinates to frontend
            result = self.sio.call('send_coords', self.sendLocation(), to=self.sid)
            counter += 1
            time.sleep(0.2)

    def enterThePark(self, desiredBattery):
        self.wantToCharge = False
        isCharged = False
        print("Entered the park " + self.name)
        result = self.sio.call('enter_park', self.sendPark(), to=self.sid)
        while self.normalSlotReserved:
            print("wait for a charger " + self.name)
            # result = self.sio.call('send_message', self.sendMessage("Waiting for a charger"), to=self.sid)
            # self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
            time.sleep(0.2)
        # result = self.sio.call('send_message', self.sendMessage("Charging"), to=self.sid)
        while True:
            if(self.battery == desiredBattery):
                break
            self.battery += 10
            if self.battery >= 1000:
                self.battery = 1000
            result = self.sio.call('send_battery', self.sendBattery(), to=self.sid)
            # self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
            time.sleep(0.2)

    def leaveThePark(self):
        print("Leaving the park " + self.name)
        self.updateEvent(event["exitPark"], self.parkId)
        self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
        result = self.sio.call('send_message', self.sendMessage("DENM - exitPark(" + str(event["exitPark"]) + ") : rsuId(" + str(self.parkId) + ")"), to=self.sid)
        self.parkLatitude = 0
        self.parkLongitude = 0
        self.parkId = None
        self.chargerSlotReserved = False
        self.normalSlotReserved = False
        result = self.sio.call('send_coords', self.sendLocation(), to=self.sid)

    def run(self):
        self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
        while True:
            if(self.parkLatitude != 0):
                self.goToThePark()
                if(self.location != self.getParkLocation(self.parkLatitude, self.parkLongitude)):
                    self.goToThePark()
                self.enterThePark(1000)
                self.leaveThePark()
            self.location += 1
            self.battery -= randint(0, 5)
            if(self.location > 135):
                self.location = 0
            self.updateLocation((float)(self.coords_json[str(self.location)]["latitude"]), (float)(
                self.coords_json[str(self.location)]["longitude"]))
            # self.mqttc.publish("vanetza/in/cam", json.dumps(self.cam))
            if(self.battery <= 250): #and not self.wantToCharge):
                print("I want to charge " + self.name)
                self.wantToCharge = True
                self.updateEvent(event["batteryStatus"], event["battery0_25"])
                self.mqttc.publish("vanetza/in/denm", json.dumps(self.denm))
                result = self.sio.call('send_message', self.sendMessage("DENM - batteryStatus(" + str(event["batteryStatus"]) + ") : battery0_25(" + str(event["battery0_25"])+ ")"), to=self.sid)
            result = self.sio.call('send_coords', self.sendLocation(), to=self.sid)
            time.sleep(0.2)
