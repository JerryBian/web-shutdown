from flask import Flask, send_from_directory, jsonify
import subprocess
import sys

app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
    return send_from_directory('', 'index.html')


@app.route('/shutdown', methods=['POST'])
def shutdown():
    command = subprocess.run(['sudo', 'shutdown', '-h', 'now'], capture_output=True)
    return jsonify({'stdout': command.stdout.decode(), 'stderr': command.stderr.decode()})

@app.route('/reboot', methods=['POST'])
def reboot():
    command = subprocess.run(['sudo', 'reboot'], capture_output=True)
    return jsonify({'stdout': command.stdout.decode(), 'stderr': command.stderr.decode()})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
