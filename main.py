#main.py

from datetime import datetime
from threading import Thread
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, disconnect

import gps

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
timethread = None
gpsthread = None
thread_lock = Lock()


def time_thread():
    print('started timer')
    while True:
        socketio.sleep(1)
        now = datetime.now()
        t = now.strftime("%H:%M:%S")
        socketio.emit('time', {'time': t})

def gps_thread():
    # Listen on port 2947 (gpsd) of localhost
    session = gps.gps()
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    print('started gps')
    while True:
        report = session.next()
        # Wait for a 'TPV' report and display the current time
        # To see all report data, uncomment the line below
        # print(report)
        if report['class'] == 'TPV':
            if hasattr(report, 'time'):
                data = {'time': report.time,
                        'lat': report.lat,
                        'lon': report.lon,
                        'track': report.track,
                        'speed': report.speed}
                with app.app_context():
                    socketio.emit('gps', render_template('gps.html', data=data))

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('my event')
def my_event(msg):
    print( msg['data'])

@socketio.event
def connect():
    global timethread, gpsthread
    with thread_lock:
        if timethread is None:
            timethread = socketio.start_background_task(time_thread)
    with thread_lock:
        if gpsthread is None:
            gpsthread = socketio.start_background_task(gps_thread)
    emit('response', {'data': 'Connected', 'count': 0})    

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
	
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
