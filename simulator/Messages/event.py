from enum import Enum


class Event(Enum):
    reserved = 0
    trafficCondition = 1
    accident = 2
    roadworks = 3
    adverseWeatherCondition_Adhesion = 6
    hazardousLocation_SurfaceCondition = 9
    hazardousLocation_ObstacleOnTheRoad = 10
    hazardousLocation_AnimalOnTheRoad = 11
    humanPresenceOnTheRoad = 12
    wrongWayDriving = 14
    rescueAndRecoveryWorkInProgress = 15
    adverseWeatherCondition_ExtremeWeatherCondition = 17
    adverseWeatherCondition_Visibility = 18
    adverseWeatherCondition_Precipitation = 19
    slowVehicle = 26
    dangerousEndOfQueue = 27
    fastVehicle = 28
    childrenPresenceOnTheRoad = 29
    vehicleIsBraking = 30
    vehicleBreakdown = 91
    postCrash = 92
    humanProblem = 93
    stationaryVehicle = 94
    emergencyVehicleApproaching = 95
    hazardousLocation_DangerousCurve = 96
    collisionRisk = 97
    signalViolation = 98
    dangerousSituation = 99

    # battery status
    batteryStatus = 31
    battery0_25 = 32
    battery25_50 = 33
    battery50_75 = 34
    battery75_100 = 35

    # park status
    parkStatus = 36
    parkFull = 37
    parkWithChangerPlace = 38
    parkWithNormalPlace = 39
