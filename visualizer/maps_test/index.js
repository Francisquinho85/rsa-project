var map, rsu1, rsu2, obu1, obu2, obu3, obu4, obu5, obu6, obu7, obu8;
var rsu1Park, rsu2Park;
var rsu1Slot0Location, rsu1Slot1Location, rsu1Slot2Location;
var rsu2Slot0Location, rsu2Slot1Location, rsu2Slot2Location;
var rsu1Slots;
var rsu2Slots;

function initMap() {
    const aveiro = { lat: 40.632728, lng: -8.65702 };
    var mapProp = {
        center: aveiro,
        zoom: 16.3,
    };
    var rsu1Location = new google.maps.LatLng(40.63563, -8.65993); 
    var rsu2Location = new google.maps.LatLng(40.62923, -8.65496); 
    var lot1Location = new google.maps.LatLng(40.63625, -8.66034); //position 7
    var lot2Location = new google.maps.LatLng(40.62750, -8.65440); //position 48
    map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
    map.setOptions({draggable: false, zoomControl: false, scrollwheel: false, disableDoubleClickZoom: true})

    rsu1Park = new google.maps.Marker({
        position: lot1Location,
        map: map,
        icon: {
            url: 'images/rsu1.png',
            scaledSize: new google.maps.Size(70, 120)
        },
    });

    rsu2Park = new google.maps.Marker({
        position: lot2Location,
        map: map,
        icon: {
            url: 'images/rsu2.png',
            scaledSize: new google.maps.Size(70, 120)
        },
    });
    rsu1Slot1Location
    
    rsu1Slot0Location = new google.maps.LatLng(40.63702, -8.66018);
    rsu1Slot1Location = new google.maps.LatLng(40.63660, -8.66018);
    rsu1Slot2Location = new google.maps.LatLng(40.63618, -8.66035);
    rsu2Slot0Location = new google.maps.LatLng(40.62859, -8.65422);
    rsu2Slot1Location = new google.maps.LatLng(40.62817, -8.65422);
    rsu2Slot2Location = new google.maps.LatLng(40.62775, -8.65442);
    rsu1Slots = new Array(3).fill("");
    rsu2Slots = new Array(3).fill("");
}

function startSim() {
    sio.emit('startSim');
    document.getElementById("startBtn").style.display = "none";
    document.getElementById("verTable").style.display = "table";

    obu1 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu-blue.png',
            scaledSize: new google.maps.Size(40, 40),
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu2 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu-green.png',
            scaledSize: new google.maps.Size(40, 40),
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu3 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu-red.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu4 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu-orange.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu5 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu-black.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu6 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu-light-pink.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu7 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu-light-blue.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu8 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu-purple.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });
}

function updateBattery(name, battery) {
    document.getElementById(name + 'batt').innerHTML = battery + '%';
}

function updateMessage(name, message, inBool) {
    if(inBool)
        document.getElementById(name + "In").innerHTML = message;
    else
        document.getElementById(name + "Out").innerHTML = message;
}

const sio = io();

sio.on('connect', () => {
    console.log('connected');
});

sio.on('disconnect', () => {
    console.log('disconnected');
});

sio.on('send_coords', (data, cb) => {
    var newLocation = new google.maps.LatLng(data.latitude, data.longitude);
    window[data.name].setPosition(newLocation);
    updateBattery(data.name, data.battery);
    cb("Success")
});

sio.on('enter_park', (data, cb) => {
    rsuString = data.rsuName + "Slots";
    var tmp;
    for(i = 0; i < window[rsuString].length; i++)
    {
        if(window[rsuString][i] == data.obuName)
            tmp = i;
    }
    slotString = data.rsuName + "Slot" + tmp + "Location";
    window[data.obuName].setPosition(window[slotString]);
    updateBattery(data.obuName, data.battery);
    updateMessage(data.obuName, "Entering the park", 0);
    cb("Success")
});

sio.on('send_battery', (data,cb) => {
    updateBattery(data.obuName, data.battery);
    cb("Success")
});

sio.on('reserve_slot', (data, cb) => {
    rsuString = data.rsuName + "Slots";
    if(data.obuName == "obuNone")
    {
        updateMessage(window[rsuString][[parseInt(data.slot)]], "Leaving the park", 0);
        window[rsuString][parseInt(data.slot)] = "";
    } 
    else if(data.changePlace)
    {
        slotString = data.rsuName + "Slot" + data.slot + "Location";
        window[rsuString][parseInt(data.slot)] = data.obuName;
        window[rsuString][2] = "";
        window[data.obuName].setPosition(window[slotString]);
        console.log(data.obuName + " changing from slot 2 to slot " + data.slot + " in " + data.rsuName);
        updateMessage(data.obuName, "Switching from slot 2 to slot " + data.slot, 0);
    }
    else 
    {
        window[rsuString][parseInt(data.slot)] = data.obuName;
        console.log("Reserve slot " + data.slot + " of " + data.rsuName + " for " + data.obuName);
        updateMessage(data.obuName, "Reserve slot " + data.slot + " of " + data.rsuName + " for " + data.obuName, 0);
    }
    cb("Success")
});