var map;
var rsu1;
var rsu2;

function initMap() {
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
            url: 'parking-icon.png',
            scaledSize: new google.maps.Size(100,100)
        } 
    });

    rsu2 = new google.maps.Marker({
        position: rsu2Location,
        map: map,
        icon: {
            url: 'parking-icon.png',
            scaledSize: new google.maps.Size(100,100)
        } 
    });
}

const sio = io();

sio.on('connect', () => {
    console.log('connected');
});

sio.on('disconnect', () => {
    console.log('disconnected');
});

sio.on('send_coords', (data, cb) => {
    var newLocation = new google.maps.LatLng(data.coords[0], data.coords[1]);
    rsu1.setPosition(newLocation);
    cb(newLocation)
});