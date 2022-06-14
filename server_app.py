# to run: gunicorn -k eventlet -w 1 --reload server_app:app

import socketio
# import threading
from simulator.main import main

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': 'visualizer/maps_test/'
})


# def send_coords_task(sid):
#     result = sio.call('send_coords', {'coords': [40.631140, -8.6585]}, to=sid)
#     print(result)
#     sio.sleep(1)
#     threading.Timer(send_coords_task(sid))


@sio.event
def connect(sid, environ):
    print(sid, 'connected')
    sio.sleep(3)
    sio.start_background_task(main, sid, sio)


@sio.event
def disconnect(sid):
    print(sid, 'disconnected')

# @sio.event
# def sum(sid, data):
#    result = data['numbers'][0] + data['numbers'][1]
#    return result
