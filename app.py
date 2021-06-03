from flask import Flask, send_from_directory, jsonify
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import subprocess
import traceback
import logging
import sys
import os
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

executor = ThreadPoolExecutor(5)
app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
    logger.info('test')
    return send_from_directory('', 'index.html')


@app.route('/shutdown', methods=['POST'])
def shutdown():
    out = err = str()
    try:
        args = ['sudo', 'shutdown', '-h', 'now']
        executor.submit(exeCmd, args)
        out = 'Machine has been shutdown successfully'
    except Exception:
        err = traceback.format_exc()
        logger.error(err)
    logger.debug('about to send response')
    return jsonify({'stdout': out, 'stderr': err})

@app.route('/reboot', methods=['POST'])
def reboot():
    out = err = str()
    try:
        args = ['sudo', 'shutdown', '-r', 'now']
        executor.submit(exeCmd, args)
        out = 'Machine has been reboot successfully'
    except Exception:
        err = traceback.format_exc()
        logger.error(err)
    logger.debug('about to send response')
    return jsonify({'stdout': out, 'stderr': err})

def exeCmd(args):
    logger.info(f'begin exec {args}')
    time.sleep(2)
    command = subprocess.run(args, capture_output=True)
    logger.info(f'end exec {args}')
    return command
    
if __name__ == '__main__':
    app.run(host=os.getenv('ENV_HOST', '127.0.0.1'), port=os.getenv('ENV_PORT', '5000'))