var map, rsu1, rsu2, obu1, obu2, obu3, obu4, obu5, obu6;

function initMap() 
{
    const aveiro = { lat: 40.632728, lng: -8.657024};
    var mapProp = {
        center: aveiro,
        zoom: 16.5,
    };
    var rsu1Location = new google.maps.LatLng(40.631190, -8.6580);
    var rsu2Location = new google.maps.LatLng(40.631180, -8.6590);
    map = new google.maps.Map(document.getElementById("googleMap"),mapProp);
    rsu1 = new google.maps.Marker({
        position: rsu1Location,
        map: map,
        icon: {
            url: 'images/parking-icon.png',
            scaledSize: new google.maps.Size(100,100)
        }, 
        id: 1
    });

    rsu2 = new google.maps.Marker({
        position: rsu2Location,
        map: map,
        icon: {
            url: 'images/parking-icon.png',
            scaledSize: new google.maps.Size(100,100)
        }, 
        id: 2
    });
}

function startSim()
{
    sio.emit('startSim');
    document.getElementById("startBtn").style.display = "none";
    document.getElementById("verTable").style.display = "table";
    obu1 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'images/car-icon.png',
            scaledSize: new google.maps.Size(100,100)
        }, 
        id: 3
    });

    obu2 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'car-icon.png',
            scaledSize: new google.maps.Size(100,100)
        }, 
        id: 4
    });

    obu3 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'car-icon.png',
            scaledSize: new google.maps.Size(100,100)
        }, 
        id: 5
    });

    obu4 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'car-icon.png',
            scaledSize: new google.maps.Size(100,100)
        }, 
        id: 6
    });

    obu5 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'car-icon.png',
            scaledSize: new google.maps.Size(100,100)
        }, 
        id: 7
    });

    obu6 = new google.maps.Marker({
        map: map,
        icon: {
            url: 'car-icon.png',
            scaledSize: new google.maps.Size(100,100)
        }, 
        id: 8
    });
}

function updateBattery(name, battery)
{
    document.getElementById(name + 'batt').innerHTML = battery + '%';
}

const sio = io();

sio.on('connect', () => 
{
    console.log('connected');
});

sio.on('disconnect', () => 
{
    console.log('disconnected');
});

sio.on('send_coords', (data, cb) => 
{
    var newLocation = new google.maps.LatLng(data.latitude, data.longitude);
    window[data.name].setPosition(newLocation);
    updateBattery(data.name, data.battery);
    cb(newLocation)
});