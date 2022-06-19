var map, rsu1, rsu2, obu1, obu2, obu3, obu4, obu5, obu6;
var rsu1Slot1Location, rsu1Slot2Location, rsu1Slot3Location;
var rsu2Slot1Location, rsu2Slot2Location, rsu2Slot3Location;


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

    rsu1Lot = new google.maps.Marker({
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

    rsu2Lot = new google.maps.Marker({
        position: lot2Location,
        map: map,
        icon: {
            url: 'images/parking-lot-icon.png',
            scaledSize: new google.maps.Size(70, 70)
        },
    });

    rsu1Slot1Location = new google.maps.LatLng(40.63602, -8.66030);
    rsu1Slot2Location = new google.maps.LatLng(40.63629, -8.66030);
    rsu1Slot3Location = new google.maps.LatLng(40.63655, -8.66030);
    rsu2Slot1Location = new google.maps.LatLng(40.62837, -8.65456);
    rsu2Slot2Location = new google.maps.LatLng(40.62837, -8.65456);
    rsu2Slot3Location = new google.maps.LatLng(40.62837, -8.65456);
    
    obu3 = new google.maps.Marker({
        position: new google.maps.LatLng(40.63625, -8.65954),
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu2 = new google.maps.Marker({
        position: new google.maps.LatLng(40.62898, -8.65522),
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });
}

function startSim() {
    sio.emit('startSim');
    document.getElementById("startBtn").style.display = "none";
    document.getElementById("verTable").style.display = "table";
    obu1 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
    });

    obu2 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
    });

    obu3 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
    });

    obu4 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
    });

    obu5 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
    });

    obu6 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(40, 40)
        },
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
    cb(newLocation)
});