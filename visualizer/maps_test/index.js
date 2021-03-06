var map, rsu1, rsu2, obu1, obu2, obu3, obu4, obu5, obu6, obu7, obu8;
var rsu1InHistory, rsu2InHistory, obu1InHistory, obu2InHistory, obu3InHistory;
var obu4InHistory, obu5InHistory, obu6InHistory, obu7InHistory, obu8InHistory;
var rsu1Park, rsu2Park;
var rsu1Slot0Location, rsu1Slot1Location, rsu1Slot2Location;
var rsu2Slot0Location, rsu2Slot1Location, rsu2Slot2Location;
var rsu1Slots;
var rsu2Slots;
var listShow;

function initMap() {
    const aveiro = { lat: 40.632728, lng: -8.65702 };
    var removePOIs =[
        {
            featureType: "poi",
            elementType: "labels",
            stylers: [
                  { visibility: "off" }
            ]
        }
    ];
    var mapProp = {
        center: aveiro,
        zoom: 16.3,
        styles: removePOIs
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
    rsu1InHistory = new Array();
    rsu2InHistory = new Array();
    obu1InHistory = new Array();
    obu2InHistory = new Array();
    obu3InHistory = new Array();
    obu4InHistory = new Array();
    obu5InHistory = new Array();
    obu6InHistory = new Array();
    obu7InHistory = new Array();
    obu8InHistory = new Array();
}

function startSim() {
    sio.emit('startSim');
    document.getElementById("startBtn").style.display = "none";
    document.getElementById("verTable").style.display = "table";
    listShow = 0;

    obu1 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu1.png',
            scaledSize: new google.maps.Size(40, 40),
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu2 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu2.png',
            scaledSize: new google.maps.Size(40, 40),
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu3 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu3.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu4 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu4.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu5 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu5.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu6 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu6.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu7 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu7.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });

    obu8 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/obu8.png',
            scaledSize: new google.maps.Size(40, 40)
        },
        zIndex: google.maps.Marker.MAX_ZINDEX
    });
}

function updateBattery(name, battery) {
    document.getElementById(name + 'batt').innerHTML = battery + '%';
}

function updateMessage(name, message) {
    document.getElementById(name + "In").innerHTML = message;
}

function updateSlots(rsu, obu, slot) {
    imageString = "images/" + obu + ".png"
    document.getElementById(rsu + "Slot" + slot).src = imageString
}

function listHistory(object) {
    var table = document.getElementById('historyTable');

    if(!listShow)
    {
        msgListStr = object.id + "History";
        msgList = window[msgListStr];
        document.getElementById('historyDiv').style.display = 'block';
        table.style.display = "block";
        
        for(i = 0; i < msgList.length; i++)
        {
            console.log(msgList[i]);
            var row = table.insertRow(0);
            row.classList.add("row100");
            var cell = row.insertCell(0);
            cell.innerHTML = msgList[i];
        }
        listShow = 1;
    } else 
    {
        document.getElementById('historyDiv').style.display = 'none';
        table.innerHTML = "";
        listShow = 0;
    }
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

sio.on('send_message', (data,cb) => {
    window[data.name + "InHistory"].unshift(data.message);
    let text = document.getElementById(data.name + "In").innerHTML;
    const oldMessage = text.split("<br>");
    let newMessage = data.message;
    newMessage += "<br>"
    newMessage += oldMessage[0];
    updateMessage(data.name, newMessage);
    cb("Success")
});

sio.on('reserve_slot', (data, cb) => {
    rsuString = data.rsuName + "Slots";
    if(data.obuName == "obuNone")
    {
        updateSlots(data.rsuName, "more", data.slot);
        window[rsuString][parseInt(data.slot)] = "";
    } 
    else if(data.changePlace)
    {
        slotString = data.rsuName + "Slot" + data.slot + "Location";
        window[rsuString][parseInt(data.slot)] = data.obuName;
        window[rsuString][2] = "";
        window[data.obuName].setPosition(window[slotString]);
        console.log(data.obuName + " changing from slot 2 to slot " + data.slot + " in " + data.rsuName);
        updateSlots(data.rsuName, "more", 2);
        updateSlots(data.rsuName, data.obuName, data.slot);
    }
    else 
    {
        window[rsuString][parseInt(data.slot)] = data.obuName;
        console.log("Reserve slot " + data.slot + " of " + data.rsuName + " for " + data.obuName);
        updateSlots(data.rsuName, data.obuName, data.slot);
    }
    cb("Success")
});