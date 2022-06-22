def getCauseCode(message):
    return message["fields"]["denm"]["situation"]["eventType"]["causeCode"]


def getSubCauseCode(message):
    return message["fields"]["denm"]["situation"]["eventType"]["subCauseCode"]


def getId(message):
    return message["fields"]["denm"]["management"]["actionID"]["originatingStationID"]

def getLatitude(message):
    return message["fields"]["denm"]["management"]["eventPosition"]["latitude"]

def getLongitude(message):
    return message["fields"]["denm"]["management"]["eventPosition"]["longitude"]