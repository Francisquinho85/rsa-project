import paho.mqtt.client as mqtt


class Car:
    def __init__(self, cam, denm, ip, name):
        self.baterry = 0
        self.latitude = 0
        self.longitude = 0
        self.cam = cam
        self.denm = denm
        self.ip = ip
        self.name = name
        self.location = 0
        self.mqttc = mqtt.Client()
        self.mqttc.connect(ip)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.loop_start()

    def updateLocation(self, coords_json):
        self.location += 1
        if(self.location > 135):
            self.location -= 136
        self.latitude = (float)(coords_json[self.location]["latitude"])
        self.longitude = (float)(coords_json[self.location]["longitude"])
        self.denm["management"]["eventPosition"]["latitude"] = self.latitude
        self.denm["management"]["eventPosition"]["longitude"] = self.longitude
        self.cam["latitude"] = self.latitude
        self.cam["longitude"] = self.longitude

    def sendLocation(self):
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def updateEvent(self, causeCode, subCauseCode):
        self.denm["situation"]["eventType"]["causeCode"] = causeCode
        self.denm["situation"]["eventType"]["subCauseCode"] = subCauseCode

    def on_connect(self, client, userdata, flags, rc):
        self.mqttc.subscribe([("vanetza/out/cam", 0), ("vanetza/out/denm", 0)])

    def on_message(self, client, userdata, msg):
        if(msg.topic == "vanetza/out/denm"):
            print("car receive denm")
        if(msg.topic == "vanetza/out/cam"):
            print("car receive cam")
        # print(msg.payload)
