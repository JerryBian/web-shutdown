from flask import Flask, send_from_directory, jsonify
from threading import Thread
import subprocess
import traceback
import logging
import os

app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
    return send_from_directory('', 'index.html')


@app.route('/shutdown', methods=['POST'])
def shutdown():
    out = err = str()
    try:
        args = ['sudo', 'shutdown', '-H', 'now']
        exeCmd(args)
        out = 'machine has been shutdown successfully'
    except Exception:
        err = traceback.format_exc()
        logging.error(err)
    return jsonify({'stdout': out, 'stderr': err})

@app.route('/reboot', methods=['POST'])
def reboot():
    out = err = str()
    try:
        args = ['sudo', 'shutdown', '-r', 'now']
        exeCmd(args)
        out = 'machine has been reboot successfully'
    except Exception:
        err = traceback.format_exc()
        logging.error(err)
    return jsonify({'stdout': out, 'stderr': err})

def exeCmd(args):
    command = subprocess.run(args, capture_output=True)
    thread = Thread(target = lambda: subprocess.run(args, capture_output=True))
    thread.start()
    return (thread, command)

if __name__ == '__main__':
    app.run(host=os.getenv('ENV_HOST', '127.0.0.1'), port=os.getenv('ENV_PORT', '5000'))