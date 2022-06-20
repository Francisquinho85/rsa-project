var map, rsu1, rsu2, obu1, obu2, obu3, obu4, obu5, obu6;
var rsu1Park, rsu2Park;
var rsu1Slot1Location, rsu1Slot2Location, rsu1Slot3Location;
var rsu2Slot1Location, rsu2Slot2Location, rsu2Slot3Location;
var rsu1Slots;
var rsu2Slots;


function initMap() {
    const aveiro = { lat: 40.632728, lng: -8.65702 };
    var mapProp = {
        center: aveiro,
        zoom: 16.3,
    };
    var rsu1Location = new google.maps.LatLng(40.63625, -8.65954); 
    var rsu2Location = new google.maps.LatLng(40.62898, -8.65522); 
    var lot1Location = new google.maps.LatLng(40.63635, -8.66034); //position 7
    var lot2Location = new google.maps.LatLng(40.62820, -8.65450); //position 48
    map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
    map.setOptions({draggable: false, zoomControl: false, scrollwheel: false, disableDoubleClickZoom: true})
    // rsu1 = new google.maps.Marker({
    //     position: rsu1Location,
    //     map: map,
    //     icon: {
    //         url: 'images/parking-icon.png',
    //         scaledSize: new google.maps.Size(60, 60)
    //     }
    // });

    rsu1Park = new google.maps.Marker({
        position: lot1Location,
        map: map,
        icon: {
            url: 'images/parking-lot-icon.png',
            scaledSize: new google.maps.Size(70, 70)
        },
    });

    // rsu2 = new google.maps.Marker({
    //     position: rsu2Location,
    //     map: map,
    //     icon: {
    //         url: 'images/parking-icon.png',
    //         scaledSize: new google.maps.Size(60, 60)
    //     }
    // });

    rsu2Park = new google.maps.Marker({
        position: lot2Location,
        map: map,
        icon: {
            url: 'images/parking-lot-icon.png',
            scaledSize: new google.maps.Size(70, 70)
        },
    });

    rsu1Slot0Location = new google.maps.LatLng(40.63602, -8.66030);
    rsu1Slot1Location = new google.maps.LatLng(40.63629, -8.66030);
    rsu1Slot2Location = new google.maps.LatLng(40.63655, -8.66030);
    rsu2Slot0Location = new google.maps.LatLng(40.62827, -8.65456);
    rsu2Slot1Location = new google.maps.LatLng(40.62837, -8.65456);
    rsu2Slot2Location = new google.maps.LatLng(40.62857, -8.65456);
    rsu1Slots = new Array(3).fill("");
    rsu2Slots = new Array(3).fill("");
}

function startSim() {
    sio.emit('startSim');
    document.getElementById("startBtn").style.display = "none";
    document.getElementById("verTable").style.display = "table";
    rsu1FreeSlots = 3;
    rsu2FreeSlots = 3;
    obu1 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu2 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu3 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu4 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu5 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu6 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });
}

function updateBattery(name, battery) {
    document.getElementById(name + 'batt').innerHTML = battery + '%';
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
    cb("Success")
});

sio.on('send_battery', (data,cb) => {
    updateBattery(data.obuName, data.battery);
    cb("Success")
});

sio.on('reserve_slot', (data, cb) => {
    rsuString = data.rsuName + "Slots";
    window[rsuString][parseInt(data.slot)] = data.obuName;
    console.log("Reserve slot " + data.slot + " of " + data.rsuName + " for " + data.obuName);
    cb("Success")
});

sio.on('leave_park', (data, cb) => {
    rsuString = data.rsuName + "Slots";
    for(i = 0; i < window[rsuString].length; i++)
    {
        if(window[rsuString][i] == data.obuName)
            tmp = i;
    }
    window[rsuString][i] = "";
    cb("Success")
});