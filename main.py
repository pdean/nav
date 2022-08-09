#main.py

from datetime import datetime
from threading import Thread
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, disconnect


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
thread_lock = Lock()

def background_thread():
    print('started background task')
    while True:
        socketio.sleep(1)
        now = datetime.now()
        t = now.strftime("%H:%M:%S")
        socketio.emit('message', {'data': 'This is data', 'time': t})


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('my event')
def my_event(msg):
    print( msg['data'])

@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})    


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
	
	
if __name__ == '__main__':
    socketio.run(app)
