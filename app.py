import asyncio
# from concurrent.futures import ProcessPoolExecutor

from sanic import Sanic
from sanic.response import html

import socketio

import sys
import os

app = Sanic()
sio = socketio.AsyncServer(async_mode='sanic')
sio.attach(app)
# pool = ProcessPoolExecutor()

recording = False


@app.route('/')
async def index(request):
    with open('app.html') as f:
        return html(f.read())


@sio.on('start recording', namespace='/test')
async def start_recording(sid):
    global recording
    print('--> start recording', sid)
    await sio.emit('started recording', {'data': 'started'}, namespace='/test')
    recording = True
    # loop = asyncio.get_event_loop()
    # await loop.run_in_executor(pool, record)
    await record()
    await sio.emit('done recording', {'data': 'done'}, namespace='/test')


@sio.on('stop recording', namespace='/test')
async def stop_recording(sid):
    global recording
    print('--> stop recording', sid)
    recording = False
    temp_path = remove_lock()
    if temp_path:
        filename = temp_path.split(os.sep)[-1]
        saved_path = os.path.join('static', 'recordings', filename)
        os.rename(temp_path, saved_path)

    await sio.emit('stopped recording', {'data': 'stopped', 'filename': '/' + saved_path}, namespace='/test')

@sio.on('load recordings', namespace='/test')
async def load_recordings(sid):
    files = os.listdir(os.path.join('static', 'recordings'))
    recordings = []
    for f in files:
        if f.endswith('.wav'):
            recordings.append('/static/recordings/{0}'.format(f))
    # print(recordings)
    await sio.emit('recordings', {'recordings': recordings}, namespace='/test')


def remove_lock():
    filename = None
    if os.path.exists('recording.lock'):
        with open('recording.lock', 'r') as f:
            filename = f.read()
        os.remove('recording.lock')
    return filename

async def record():
    print('starting subprocess to record')
    process = await asyncio.create_subprocess_exec(
        './venv/bin/python',
        'rec_unlimited.py',
        # stdin must a pipe to be accessible as process.stdin
        stdin=asyncio.subprocess.PIPE,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE)
    # Write message
    # print('Writing {!r} ...'.format(msg))
    # process.stdin.write(msg.encode() + b'\n')
    # Read reply
    # data = await process.stdout.readline()
    # reply = data.decode().strip()
    # print('Received {!r}'.format(reply))
    # Stop the subprocess
    # process.terminate()
    # code = await process.wait()
    # print('Terminated with code {}'.format(code))

# def touch(fname):
#     with open(fname, 'a'):
#         os.utime(fname)

# def record():
#     # global recording
#
#     import sounddevice as sd
#     import soundfile as sf
#     import queue
#     import tempfile
#
#     touch('recording.lock')
#
#     devices = sd.query_devices()
#     device_info = sd.query_devices(None, 'input')
#     samplerate = int(device_info['default_samplerate'])
#     filename = tempfile.mktemp(prefix='rec_unlimited_',
#                                     suffix='.wav', dir='')
#     channels = 1
#     subtype = None
#     device = None
#
#     print('recording data', samplerate, filename)
#
#     q = queue.Queue()
#     # q = asyncio.Queue()
#
#
#     def callback(indata, frames, time, status):
#         """This is called (from a separate thread) for each audio block."""
#         if status:
#             print('!!status', status, file=sys.stderr)
#         q.put(indata.copy())
#
#
#     # Make sure the file is opened before recording anything:
#     with sf.SoundFile(filename, mode='x', samplerate=samplerate,
#                       channels=channels, subtype=subtype) as file:
#         print('opened sound file')
#         with sd.InputStream(samplerate=samplerate, device=device,
#                             channels=channels, callback=callback):
#             print('opened input stream')
#             print('#' * 80)
#             print('press Ctrl+C to stop the recording')
#             print('#' * 80)
#             while os.path.exists('recording.lock'):
#                 file.write(q.get())


async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        count += 1
        await sio.emit('my response', {'data': 'Server generated event'},
                       namespace='/test')


@app.listener('before_server_start')
def before_server_start(sanic, loop):
    sio.start_background_task(background_task)







@sio.on('my event', namespace='/test')
async def test_message(sid, message):
    await sio.emit('my response', {'data': message['data']}, room=sid,
                   namespace='/test')


@sio.on('my broadcast event', namespace='/test')
async def test_broadcast_message(sid, message):
    await sio.emit('my response', {'data': message['data']}, namespace='/test')


@sio.on('join', namespace='/test')
async def join(sid, message):
    sio.enter_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': 'Entered room: ' + message['room']},
                   room=sid, namespace='/test')


@sio.on('leave', namespace='/test')
async def leave(sid, message):
    sio.leave_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': 'Left room: ' + message['room']},
                   room=sid, namespace='/test')


@sio.on('close room', namespace='/test')
async def close(sid, message):
    await sio.emit('my response',
                   {'data': 'Room ' + message['room'] + ' is closing.'},
                   room=message['room'], namespace='/test')
    await sio.close_room(message['room'], namespace='/test')


@sio.on('my room event', namespace='/test')
async def send_room_message(sid, message):
    await sio.emit('my response', {'data': message['data']},
                   room=message['room'], namespace='/test')


@sio.on('disconnect request', namespace='/test')
async def disconnect_request(sid):
    await sio.disconnect(sid, namespace='/test')


@sio.on('connect', namespace='/test')
async def test_connect(sid, environ):
    await sio.emit('my response', {'data': 'Connected', 'count': 0}, room=sid,
                   namespace='/test')


@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')


app.static('/static', './static')


if __name__ == '__main__':
    app.run(
        debug=True
    )
